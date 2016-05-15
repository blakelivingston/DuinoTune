#include <DuinoTune.h>
#include <tinytune/zelda.h>
void setup() {
  // put your setup code here, to run once:
  initTinyTune();
  playSong(&zelda);
}

void loop() {
  // put your main code here, to run repeatedly:

}
