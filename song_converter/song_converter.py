import xrns2tt
try:
    from tkinter import *
    try:
        import ttk
    except:
        import tkinter.ttk as ttk
    try:
        import tkFileDialog
    except:
        import tkinter.filedialog as tkFileDialog
except:
    from Tkinter import *
    import tkFileDialog
    import ttk
import time

import threading
from os import stat,listdir
import os.path as path
import errno
import os
import traceback

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def song_convert_watcher():
    running = True
    root = Tk()
    root.title("Renoise -> DuinoTune converter")

    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    # feet = StringVar()
    # meters = StringVar()
    out_dir = StringVar()
    in_dir = StringVar()
    def save_state():
        open(".songconverterstate", "w+").write("%s\n%s" %(in_dir.get(), out_dir.get()))

    def load_state():

        try:
            indir, outdir = map(lambda x:x.strip() ,open(".songconverterstate", "r").readlines())
            in_dir.set(indir)
            out_dir.set(outdir)
        except IOError:
            pass

    load_state()
    def pick_in_dir():
        in_dir.set(tkFileDialog.askdirectory())
        save_state()

    def pick_out_dir():
        out_dir.set(tkFileDialog.askdirectory())
        save_state()

    ttk.Label(mainframe, text="Input Song Directory:").grid(column=1, row=1, sticky=W)
    ttk.Label(mainframe, textvariable=in_dir).grid(column=2, row=1, sticky=W)
    ttk.Label(mainframe, text="Output Song Directory:").grid(column=6, row=1, sticky=E)
    ttk.Label(mainframe, textvariable=out_dir).grid(column=7, row=1, sticky=W)
    ttk.Button(mainframe,text='Pick Input Directory', command=pick_in_dir).grid(column=1, row=2, sticky=N)
    ttk.Button(mainframe,text='Pick Output Directory', command=pick_out_dir).grid(column=6, row=2, sticky=N)
    # ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)
    for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
    tlog = Text(mainframe, wrap="word", width=100)
    tlog.grid(column=1, columnspan=9, row=4 ,rowspan=7, sticky=W)

    def songWatcher():
        while running:
            try:
                if in_dir.get() and out_dir.get():
                    song_stats= [(path.join(in_dir.get(),f),stat((path.join(in_dir.get(),f))).st_mtime)
                        for f in  listdir(in_dir.get()) if f.endswith(".xrns")]

                    for songfile, modtime in song_stats:
                        song_basename = path.splitext(path.basename(songfile))[0]
                        out_path = path.join(out_dir.get(), song_basename, "src")
                        mkdir_p(out_path)
                        out_path_songname=path.join(out_path, song_basename)
                        if path.exists(out_path_songname + ".c"):
                            out_song_mtime = stat(out_path_songname + ".c").st_mtime
                        else:
                            out_song_mtime = 0
                        if modtime > out_song_mtime:
                            tlog.insert("1.0", "Song: %s changed.\nUpdated Arduino library at: %s\n" % (
                            songfile, out_path_songname))
                            # The song has been changed Re-export!!
                            xrns2tt.xrns_to_tt(songfile, out_path_songname, {})
                            write_library_file(out_dir.get(), song_basename)
            except Exception as e:
                tlog.insert("1.0", "Error translating song: %s\n Trace: %s\n" % (e, traceback.format_exc()))
            time.sleep(1)

    threading.Thread(target=songWatcher).start()
    root.mainloop()
    running = False

def write_library_file(out_dir, songname):
    lib_prop="""name=%s
version=0.9
author=You! <you@not.real.email.com>
maintainer=You! <you@not.real.email.com>
sentence=Auto Generated DuinoTune Song Library
paragraph=Auto Generated DuinoTune Song Library
category=Data Storage
url=http://example.com/
architectures=avr
""" % songname
    ofile = open(path.join(out_dir, songname, "library.properties"), "w+")
    ofile.write(lib_prop)
    ofile.close()


if __name__ == "__main__":
    song_convert_watcher()
