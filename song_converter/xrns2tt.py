#!/usr/bin/env python
from xml.etree import ElementTree
import glob
import optparse
import os
import sys
import zipfile

class Inst(object):
    env_tpl = """
  static int16_t slopes_%d[] = {%s};
  static uint8_t pticks_%d[] = {%s};
  static struct TTENVELOPE env_%d = {
    .num_points = %d,
    .starting_level = %d,
    .env_slopes = slopes_%d,
    .point_ticks = pticks_%d,
    .sustain_tick = %d
  };
  """
    inst_tpl = """
static struct TTINSTRUMENT inst_%d = {
    .voice_type=%d,
    .duty=%d,
    .bitcrush=%d,
    .envelope=%s
};
    """

    def __init__(self):
        self.has_env = False
        self.has_voice = False
        self.type = 0;
        self.duty = 0x80
        self.bitcrush = 8

    type_to_voice_type_enum = {
        "SQR": 0,
        "TRI": 1,
        "NOISE": 2
    }
    def parse_voice_from_name(self, vname):
        if len(vname.split('_')) >= 3:
            self.has_voice = True
            type, duty, bitcrush = vname.split('_')[:3]
            self.type = self.type_to_voice_type_enum[type]
            self.duty = int(duty, 16)
            self.bitcrush = int(bitcrush)

    def parse(self, env, tpl, lpb):
        def beats_to_songticks(b):
            return (b / 256.0) * tpl * lpb

        if env.find('IsActive/Value').text =="1.0":
            self.active = True
            self.has_env = True
        else:
            return
        if env.find('SustainIsActive').text == 'true':

            self.sustain = True
            self.sustain_pt = int(env.find('SustainPos').text)
            self.sustain_pt = int(beats_to_songticks(self.sustain_pt))
        else:
            self.sustain = False
            self.sustain_pt = 255

        env_ticks = []
        levels = []
        for point in env.find('Nodes/Points'):
            tick, level = point.text.split(',')
            tick = int(tick)
            levels.append(float(level))
            # Envelope ticks are NOT song ticks.
            # there are 24 env ticks per beat.
            env_ticks.append(int(beats_to_songticks(tick)))
        self.slopes = [0]
        if env_ticks[0] != 0:
            self.tick_deltas = [env_ticks[0]]
            self.slopes = [0]
        else:
            self.tick_deltas = []
            self.slopes = []
        self.start_level = int(levels[0] * 255)
        for i in range(1, len(levels)):
            d = levels[i] - levels[i - 1]
            t_d = env_ticks[i] - env_ticks[i - 1]
            # We're rolling 9.7 bit fixed point on the slopes.
            if t_d > 0:
                self.slopes.append((int(d * 255) << 7) / t_d)
                self.tick_deltas.append(t_d)

    def c_dump(self, env_idx):
        dump = ""
        if self.has_env:
            slopes = ", ".join((str(sl) for sl in self.slopes))
            pticks = ", ".join((str(min(pt, 255)) for pt in self.tick_deltas))
            dump += self.env_tpl % (env_idx, slopes,
                                   env_idx, pticks,
                                   env_idx,
                                   len(self.slopes),
                                   self.start_level,
                                   env_idx, env_idx,
                                   self.sustain_pt)
        dump += self.inst_tpl % (env_idx,
                                 self.type,
                                 self.duty,
                                 self.bitcrush,
                                 ("&env_%d" % env_idx) if self.has_env else '0' )
        return dump

def xrns_to_tt(input_file,
               output_base,
               track_tunings):
    zf = zipfile.ZipFile(input_file)
    song = ElementTree.fromstring(zf.read('Song.xml'))
    zf.close()
    track_info = song.find('Tracks')
    t_idx = 0
    active_tracks = set()
    print ("converting %s" % input_file)
    bpm = int(song.find('*/BeatsPerMin').text)
    lpb = int(song.find('*/LinesPerBeat').text)
    tpl = int(song.find('*/TicksPerLine').text)

    for t in track_info:
        if t.find('State').text == "Active":
            active_tracks.add(t_idx)
        t_idx += 1

    xpatterns = song.find('PatternPool/Patterns')

    patterns = []

    song_instruments = song.find('Instruments')
    instruments = []
    inst_remap = {}

    for inst_id, inst in enumerate(song_instruments):
        # print inst.tag,[(x.tag,x.text) for x in list(inst)]
        vol_env = inst.find('.//SampleEnvelopeModulationDevice')
        name = inst.find('.//Name')
        if (name is not None) or (vol_env is not None):
            inst = Inst()
            if (name is not None):
                inst.parse_voice_from_name(name.text)
            if vol_env is not None:
                inst.parse(vol_env, tpl, lpb)
            if inst.has_env or inst.has_voice:
                inst_remap[inst_id] = len(instruments)
                instruments.append(inst)

    total_notes = 0

    for xpat in xpatterns:
        nlines = xpat.find('NumberOfLines')
        if nlines is None:
            continue
        nlines = int(nlines.text)
        tracks = xpat.find('Tracks')

        notelines = [[None for t in range(len(tracks))] for l in range(nlines)]
        tracknum = 0
        for track in tracks:
            if not tracknum in active_tracks:
                tracknum += 1
                continue
            lines = track.find('Lines')
            if lines is None:
                tracknum += 1
                continue
            for line in lines:
                line_index = int(line.get('index'))
                nc = line.find('*/NoteColumn')
                fc = line.find('*/EffectColumn')
                if nc is not None or fc is not None:
                    if line_index >= nlines:continue
                    total_notes += 1
                    notelines[line_index][tracknum] = (nc, fc)
            tracknum += 1
        patterns.append(notelines)

    sequence = []
    seq = song.find('*/SequenceEntries')
    for se in seq:
        pat = int(se.find('Pattern').text)
        if pat < len(patterns):
            sequence.append(int(se.find('Pattern').text))

    active_patterns = list(set(sequence))
    active_patterns.sort()
    pattern_remap = dict((j, i) for i, j in enumerate(active_patterns))

    sequence = [pattern_remap[s] for s in sequence]

    NOTE_ON = 0
    NOTE_OFF = 1
    ROW_ADV = 3
    SET_VOL = 4
    SET_INST = 5
    SET_GLIDE_SPEED = 6
    PORTAMENTO = 7
    NOTE_ON_FULL_VOL = 8
    ttcode_patterns = []

    def mkcode(voice, code):
        return ((voice & 0xf) << 4) + code

    nlist = {'C-' : 12,
             'C#' : 13,
             'D-' : 14,
             'D#' : 15,
             'E-' : 16,
             'F-' : 17,
             'F#' : 18,
             'G-' : 19,
             'G#' : 20,
             'A-' : 21,
             'A#' : 22,
             'B-' : 23,
             'B#' : 24}

    def note_to_num(note):
        n = note[0:2]
        octave = int(note[2])
        return 12 * octave + nlist[n]

    def calcPitchGlideMult(glide_speed, tpb):
        # Pitch glides are in 1/16 semitone per line
        # Applied each tick.
        # We don't want to do this on the mcu, so we convert it
        # to fixed point here.
        return int(0x10000 * (2 ** (((glide_speed / 16.0) / 12.0) / tpb) - 1))

    for p_idx in range(len(patterns)):
        if not p_idx in active_patterns:
            continue
        cur_pat = patterns[p_idx]
        tt_pat = []
        last_note_line = 0
        # Instruments are set at the beginning of the pattern and on change.
        # If there's an envelope at least.
        active_instruments = {}
        track_volumes = {}
        for l_idx in range(len(cur_pat)):
            tt_line = []
            cur_line = cur_pat[l_idx]
            fxval = 0
            for t_idx in range(len(cur_line)):
                cnote = cur_line[t_idx]
                if cnote is None or t_idx not in active_tracks:
                    continue
                note, fx = cnote
                if fx is not None:
                    fxcode = None
                    for elem in fx:
                        if elem.tag == "Number":
                            fxcode = elem.text
                        if elem.tag == "Value":
                            fxval = int(elem.text, 16)
                    if fxcode == "0G":
                        if fxval != 0:
                            tcode = mkcode(t_idx, SET_GLIDE_SPEED)
                            tt_line.append(tcode)
                            glide_mult = calcPitchGlideMult(fxval, tpl)
                            tt_line.append(glide_mult & 0xff)
                            tt_line.append(glide_mult >> 8)
                        tcode = mkcode(t_idx, PORTAMENTO)
                        tt_line.append(tcode)
                if note is None:
                    continue
                note_val = None
                volume = None
                inst = None
                for elem in note:
                    if elem.tag == 'Note':
                        if elem.text == 'OFF':
                            tcode = mkcode(t_idx, NOTE_OFF)
                            tt_line.append(tcode)
                        else:
                            if elem.text != '---':
                                note_val = note_to_num(elem.text)
                                note_val += track_tunings.get(t_idx, 0)
                                track_volumes[t_idx] = 0xff
                                volume = 0xff
                    if elem.tag == 'Instrument':
                        if elem.text != '..':
                            i = int(elem.text, 16)
                            if active_instruments.get(t_idx, -1) != i and i in inst_remap:
                                active_instruments[t_idx] = i
                                inst = inst_remap[i]
                    if elem.tag == 'Volume':
                        if elem.text != '..':
                            v = int(elem.text, 16) * 2
                        else:
                            v = 0xff

                        if v is not None and track_volumes.get(t_idx, -1) != v:
                            track_volumes[t_idx] = v
                            volume = v
                        else:
                            volume = None
                        # print "VOLv",volume, t_idx, v,track_volumes
                if (note_val is not None or
                    volume is not None or
                    inst is not None):
                    if inst is not None:
                        tcode = mkcode(t_idx, SET_INST)
                        tt_line.extend([tcode, inst])
                    if note_val is not None:
                        tcode = mkcode(t_idx, NOTE_ON)
                        if volume == 0xff:
                            tcode = mkcode(t_idx, NOTE_ON_FULL_VOL)
                            volume = None
                        else:
                            tcode = mkcode(t_idx, NOTE_ON)
                        if volume is not None:
                            note_val |= 0x80
                            tt_line.extend([tcode, note_val])
                            tt_line.append(volume)
                            volume = None
                        else:
                            tt_line.extend([tcode, note_val])
                    if volume is not None:
                        if volume == 0:
                            tcode = mkcode(t_idx, NOTE_OFF)
                            tt_line.append(tcode)
                        else:
                            tcode = mkcode(t_idx, SET_VOL)
                            tt_line.extend([tcode, volume])
            if tt_line:
                # we have line data!
                l_advance = l_idx - last_note_line
                last_note_line = l_idx
                while l_advance:
                    adv = (l_advance - 1) & 0xf
                    # insert row advances until the gap is covered
                    tt_pat.append(mkcode(adv, ROW_ADV))
                    l_advance -= adv + 1
                tt_pat.extend(tt_line)
        tt_pat.extend(tt_line)
        l_advance = 1 + (l_idx - last_note_line)

        while l_advance:
            adv = (l_advance - 1) & 0xf
            # insert row advances until the pattern is done.
            tt_pat.append(mkcode(adv, ROW_ADV))
            l_advance -= adv + 1
        ttcode_patterns.append(tt_pat)

    c_modulename = output_base + ".c"
    h_modulename = output_base + ".h"

    song_name = os.path.basename(output_base)

    c_outfile = open(c_modulename, 'w+')
    h_outfile = open(h_modulename, 'w+')

    c_tmpl = """
  #include "tinytune/tinytune.h"
  // Envelopes
  %s
  // Patterns
  %s

  static const uint8_t* const p_dat[] PROGMEM = {%s};
  static const uint16_t p_len[] PROGMEM = {%s};
  static const uint8_t p_ord[] PROGMEM = {%s};
  static const struct TTINSTRUMENT* instruments[] = {%s};
  struct song_definition %s = {
  .pattern_data = p_dat,
  .num_patterns = %d,
  .pattern_lengths = p_len,
  .pattern_order = p_ord,
  .bpm = %s,
  .rows_per_beat = %s,
  .ticks_per_row = %s,
  .instruments = instruments,
  };
    """

    h_tmpl = """#ifndef __%s__
  #include "tinytune/tinytune.h"
  extern struct song_definition %s;
  #endif
  """

    pattern_output = []
    pattern_lengths = []
    for tt_pat in ttcode_patterns:
        tt_lines = []
        pattern_lengths.append(len(tt_pat))
        while tt_pat:
            tt_l = tt_pat[0:20]
            tt_pat = tt_pat[20:]
            tt_lines.append(', '.join(["%u" % d for d in tt_l]))
        pattern_output.append(tt_lines)

    pat_defs = "\n".join(["static const uint8_t pattern_%d[] PROGMEM = {\n%s\n};" % (pid, ',\n'.join(data))
                          for pid, data in enumerate(pattern_output)])

    inst_defs = "\n".join(e.c_dump(idx) for idx, e in enumerate(instruments))

    c_output = c_tmpl % (inst_defs, pat_defs, ",\n".join(
        ["pattern_%d" % i for i in range(len(pattern_output))]),
        ", ".join([str(l) for l in pattern_lengths]),
        ", ".join([str(l) for l in sequence]),
        ", ".join(["&inst_%d" % i for i in range(len(instruments))]),
        song_name,
        len(sequence),
        bpm,
        lpb,
        tpl)

    c_outfile.write(c_output)
    c_outfile.close()

    h_output = h_tmpl % (song_name.upper(), song_name)
    h_outfile.write(h_output)
    h_outfile.close()

if __name__ == "__main__":
    option_parser = optparse.OptionParser(usage="usage: %prog [options] input.xrns [input2.xrns input3.xrns ...]\n")
    option_parser.add_option("--tuning_dict", dest="tuning", action="store",
                       type="string", default=None,
                       help="Per-channel tuning offset. E.g. "
                       "{0: -4, 1: -4, 3: -37, 4: -21, 5: -21}")
    options, values = option_parser.parse_args(sys.argv)

    if len(values) < 2:
        print (option_parser.print_usage())
        sys.exit()
    if options.tuning:
        track_tunings = eval(options.tuning)
    else:
        track_tunings = {}
    for input_file in values[1:]:
        for exp_file in glob.glob(input_file):
            output_base = os.path.basename(os.path.splitext(exp_file)[0])
            xrns_to_tt(exp_file, output_base, track_tunings)
