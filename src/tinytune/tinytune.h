#ifndef __TINYTUNE__
#define __TINYTUNE__
#ifdef __cplusplus
extern "C" {
#endif

// Code definitions for song events
#define NOTE_ON 0
#define NOTE_OFF 1
#define ROW_ADV 3
#define SET_VOL 4
#define SET_INST 5
#define SET_GLIDE_SPEED 6
#define PORTAMENTO 7
#define NOTE_ON_FULL_VOL 8

#include <avr/pgmspace.h>
#include <inttypes.h>

typedef char bool;
typedef uint8_t* PROGMEM songdata;

// forward declarations
struct TTENVELOPE;
struct TTINSTRUMENT;
struct song_definition;

// Initializes the system. This must be called before any synthesis can occur.
// It uses the PWM registers and Timer1
// Output is on PIN 3 (OC1B)
void initTinyTune(void);

// Voices are indexed from 0 up to N_VOICES
// Sets the voice to PWM audio output
void initVoicePWM(uint8_t voice);

// Sets the voice to triangle/saw audio output
void initVoiceTRI(uint8_t voice);

// Sets the voice to noise output
void initVoiceNOISE(uint8_t voice);

// The following voice modifiers can be called at any time.
// Sets the volume on a voice.
void setVolume(uint8_t voice, uint8_t volume);

/*	Sets the Duty cycle on a voice. For PWM this implies the ratio of high/low, as
	a ratio of duty/255. For triangle waves, values between 0 - 255 
	transition between TRI and SAW waves.
*/
void setDuty(uint8_t voice, uint8_t duty);

// Sets the pitch of a voice in Hz
void setPitch(uint8_t voice, uint16_t pitch);

// Enables/disables a voice. This must be set to true to hear anything for a voice.
void setEnable(uint8_t voice, bool enable);

/* 	Sets the bit-wise quantization for a voice. E.g,  crunch=3,
	would quantize the voice to 8 - 3 = 5-bits.
	crunch=0 disables this.
	Sounds most distinctive on TRI waves. Compare crunch=4 to the TRI channel on an NES.
*/
void setBitCrunch(uint8_t voice, uint8_t crunch);


// The following only function during song playback

// Sets the envelope to use during song playback on this channel.
void setEnvelope(uint8_t voice, const struct TTENVELOPE* envelope);

void setInstrument(uint8_t voice, const struct TTINSTRUMENT* instrument);

/*	Sets the portamento rate on this voice. p_rate is a 12.4 fixed point frequency
	multiplier applied per song tick.
*/
void setPortaRate(uint8_t voice, uint16_t p_rate);
// Enables or disables pitch portamento on this voice.
void setPorta(uint8_t voice, bool enable);

// Waits for ms milliseconds, using the sample clock.
void waitMS(uint16_t ms);

// Plays back a song, in the background defined by song_def
void playSong(struct song_definition* song_def);


// Internal data structures.

typedef struct TTENVELOPE {
  int8_t num_points;
  // Fixed point 9.7 starting volume;
  uint8_t starting_level;
  // Fixed point slopes 9.7
  int16_t* env_slopes;
  // Number of ticks to run each slope.
  uint8_t* point_ticks;
  // Tick to halt envelope until note off.
  uint8_t sustain_tick;
} TTENVELOPE;

typedef struct TTINSTRUMENT {
	uint8_t voice_type;
	uint8_t duty;
	uint8_t bitcrush;
	TTENVELOPE* envelope;
} TTINSTRUMENT;

struct TTVOICE {
  enum {
    TT_PWM, TT_TRI, TT_NOISE
  } voice_type;

  // Integer hz.
  uint16_t hz;
  // Fractional hz for portamento accuracy. 0.4 fp.
  uint8_t f_hz;
  // Volume.
  uint8_t volume;
  int8_t _s_volume;
  // Fixed 9.7 envelope volume
  int16_t _env_volume;
  // Index of the current envelope's progress
  uint8_t _env_idx;
  // Number of ticks remaining on the current envelope node.
  uint8_t _env_ticks_left_for_node;
  //total env_ticks
  uint8_t _env_ticks;
  // Have we hit the sustain_pt?
  uint8_t sustaining;
  uint8_t gliding;
  uint16_t porta_rate;
  uint16_t porta_pitch;

  const struct TTENVELOPE* _envelope;
  // Voice enabled
  bool enabled;
  uint16_t _period;
  // error term.
  uint16_t _err;
  uint16_t bcrunch;
  void (*_getSample)(struct TTVOICE*);
  void (*_setVolume)(struct TTVOICE*, uint8_t);
  void (*_setDuty)(struct TTVOICE*, uint8_t duty);
  void (*_setPitch)(struct TTVOICE*, uint16_t pitch);
  void (*_setEnable)(struct TTVOICE*, bool enable);
  union {
    struct {
      uint8_t duty;
      uint16_t duty_period;
    } pwm;
    struct {
      uint8_t duty;
      uint16_t rise_period;
      // 9.7 bit fixed point.
      int16_t fp_vol;
      int16_t level;
      int16_t rise_slp;
      int16_t fall_slp;
    } tri;
  } _params;
};

struct song_definition {
  const uint8_t* const * pattern_data;
  const uint16_t* pattern_lengths;
  uint8_t num_patterns;
  const uint8_t* pattern_order;
  uint16_t bpm;
  uint8_t rows_per_beat;
  uint8_t ticks_per_row;
  const struct TTINSTRUMENT** instruments;
};

struct song_info {
  uint16_t samples_per_tick;
  uint16_t tick;
  uint16_t next_tick;
  uint16_t tick_smp_count;
  struct song_definition* song_def;
  uint8_t cur_pattern;
  uint8_t order_idx;
  uint16_t pat_idx;
  bool playing;
} song_info;


#ifdef __cplusplus
}
#endif
#endif
