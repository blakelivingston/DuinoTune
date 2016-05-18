// CPU clock rate
// #define F_CPU 8000000
// Number of bytes to pre-calculate. Not conclusively shown that this helps much.
// Use even numbers unless you like high pitched howls.
#define SAMPLE_BUFFER 16
// Sample clock updates at this rate in Hz
// Go ahead and abuse this number in the 55000 and above range if you get bored. Glitches may combine
// amusingly with sample buffer size changes. It's like the chip will break.
// Some sounds take on an almost vocal quality in their distortion at 65000hz
#if defined (__AVR_ATtiny85__)
#define SAMPLE_RATE 14000UL
#endif

#if defined (__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
#define SAMPLE_RATE 31000UL
#endif
// Max number of voices
#define N_VOICES 5
// Right shift divide for output waveform. Use for course global volume setting
#define OUTPUT_SCALE_SHIFT 3
