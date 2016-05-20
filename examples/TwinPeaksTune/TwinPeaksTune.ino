
#include <DuinoTune.h>
#include <twinpeaks.h>
#include "Arduino.h"

void setup()
{
  initTinyTune();
  playSong(&twinpeaks);
}

void loop()
{
}
