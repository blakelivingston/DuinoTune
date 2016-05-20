
#include <DuinoTune.h>
#include <faxanadu.h>
#include "Arduino.h"

void setup()
{
  initTinyTune();
  playSong(&faxanadu);
}

void loop()
{
}
