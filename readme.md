DuinoTune
===

DuinoTune is a multi-voice, mult-timbral audio synthesis, song playback/embedding library targeting the AVR based Arduinos, requiring minimal additional electronic components for use in projects. Tested and working on Arduino Uno and Duemilanove (ATmega328P), Arduino Leonardo (ATMega32U-4), and Adafruit Trinket (ATtiny85).

What Exactly Does It Do?
---

The  library consists of two somewhat independent parts; A multi-voice synthesizer that uses Fast PWM to simulate 8-bit analog output, and an interrupt driven background-song playback system that plays note and controller data out of chip Flash memory (progmem).

There is also an import utility that generates embeddable code representations of songs, using the save files of the [Renoise](http://www.renoise.com/) tracker-based music composition program as input. Renoise offers a demo version that is usable with this project; though I heartily encourage supporting their excellent software if you find it useful.

Example video, running into an oscilloscope: <a href="https://www.youtube.com/watch?v=PtxxCKs822M">https://www.youtube.com/watch?v=PtxxCKs822M</a>

Another Example: [https://www.youtube.com/watch?v=G3baH5iTcFM](https://www.youtube.com/watch?v=G3baH5iTcFM)
Features
---

### Hardware

* Minimal configuration is playback through PWM Pin 3 directly to powered speakers. It sounds nicer with a low pass filter.

* Requires only an external resistor for  driving small headphones

* A resistor capacitor lowpass filter can be used to smooth the PWM output into a reasonably clean audio signal, suitable for driving small headphones or input into an amplifier circuit.

### Synthesis
* Can play as many simultaneous voices as the CPU speed and RAM can accommodate
* Offers the following voice types:
	* PWM (square wave), with adjustable duty cycle
	* Triangle/Saw wave, continuously adjustable between the two waveforms (use the duty cycle setting)
	* Noise channel.
* Adjustable playback volume
* Interrupt based, and can run in the background
* Bit Crush
	* Reduces output waveform bit depth. Makes most sense on triangle waves. Try a BitCrush of 4 on a TRI wave for that old-school NES triangle wave sound.

### Song playback
* Arbitrary envelopes, including sustain and release. Just add a Volume Envelope to the instrument in Renoise.
* Portamento and pitch-glides
* Pattern based playback, for space efficiency
	*repeated patterns of music do not take much additional Flash ram
* Song size limited mostly by Flash capacity
* Interrupt based, and can run in the background

### Renoise import
* Supports arbitrary pattern lengths
* Instrument envelope import
* Imports pitch glide and bend commands


Documentation and Demos
---

### Getting Started
DuinoTune is built to be super easy to use! There are, however, a few dependencies needed to use it.

* Download [Python 2.7](https://www.python.org/downloads/) and install - this is needed for song conversion.
* Download [Renoise Demo 3.1](http://renoise.com/download) and install - this is used for song editing.
* Install the DuinoTune library into your Arduino libraries folder. On windows this is usually in `Documents\Arduino\Libraries` of your home directory. 
	* You can install by cloning from GitHub, or by Downloading a zip and unzipping it into the library folder.

There is a video walk-through to help get started on YouTube: [https://www.youtube.com/watch?v=mtrslXPgELw](https://www.youtube.com/watch?v=mtrslXPgELw)

### Playing a Demo Song
* Set up a sketch for your Arduino
	* You should now see DuinoTune as one of the options in the Arduino IDE when you go to the Sketch/Include Library menu. If not, check to make sure that it is in your arduino library folder.
	* Adding the library will automatically include DuinoTune.h. **Make sure that this is included before any of the song header files, and not after! Otherwise compilation will fail.**
* Start up the song converter utility
	* Go to the DuinoTune library folder that you just downloaded. Inside, there will be a `song_converter` folder. Go there and run `song_converter.py`. It should open a window when double clicked if python is installed properly.
	* Once the converter window opens. Click on the `Pick Output Directory` button - then choose your Arduino Library Folder, probably: `Documents\Arduino\Libraries`
	* Next click the Pick Input Directory button and choose the `test_songs` folder under DuinoTune

Once this is done, the converter should find your songs and generate Arduino Libraries for them. As long as this utility is open, changes to the songs will automatically update the libraries. That is, if you save your song in Renoise, the next time you build and upload your sketch it will be updated.

Now that the libraries are created, go back to your Sketch. In the Sketch/Include Library menu, you should now see Contributed Libraries for the songs!

Pick the Zelda song (or another, if you like) library. This will include zelda.h, but you may need to move this include line to after DuinoTune.

Now, update your setup function to include DuinoTune's initialization and start song playback. Your sketch will probably look something like this:


	#include <DuinoTune.h>
	#include <zelda.h>
	#include "Arduino.h"
	
	//The setup function is called once at startup of the sketch
	void setup()
	{
	// Add your initialization code here
		initTinyTune(); // It used to be called TinyTune, before porting to arduino
		playSong(&zelda);
	}
	
	// The loop function is called in an endless loop
	void loop()
	{
	//Add your repeated code here
	}

**That's it!** Upload your sketch, and connect PWM pin 3 to a powered speaker or small set of headphones, through a ~125ohm resistor, and listen!

Song playback occurs in the background on timer interrupts so the loop function can still be used for your projects! Songs can also be started from within the Loop.


### Controlling the Synthesizer
For help in controlling the library directly see [src/tinytune/tinytune.h](src/tinytune/tinytune.h) for per-function comments.

### Composing with Renoise

TBD


Limitations
---
* Noise channel only supports 4-bit volume on ATtiny85 (life is hard without hardware multiply)
* Not all envelope parameters are supported (no loops)
* Output pin is hard-coded to Pin 3 (OC1B) - changeable with some hacking
* Envelopes and pitch bends will only function while a 'song' is playing, initiated by playSong(). For non-song audio synthesis, the caller will have to change volumes and pitches as needed.

Hacking
---
This is a hobby project, and my MCU and electronics experience could always use input. Feel free to make suggestions, point out document errors and unclearness. Patches and additions welcome!

Also feel free to drop me a line if you use this library! I'm always curious to see how it 
comes in handy. My original intent was to augment [one of these guys](http://www.otamatone.com/) with super enhanced sound, but I still haven't gotten around to it.

License
---
This project is provided under an [MIT License](LICENSE)
