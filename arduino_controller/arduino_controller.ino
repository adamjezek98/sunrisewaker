#include "FastLED.h"


#define NUM_LEDS 120

#define DATA_PIN 3


// Define the array of leds
CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS);
  Serial.begin(115200);
}
#define del 100
void loop() {
  if (Serial.available()) {

    Serial.readStringUntil('s'); //get rid off everything before start

    String com = Serial.readStringUntil(':');
    switch (com[0]) {
      case 'l': //lit by color
        {
          int r = Serial.readStringUntil(':').toInt();
          int g = Serial.readStringUntil(':').toInt();
          int b = Serial.readStringUntil(':').toInt();

          fill_solid( leds, NUM_LEDS, CRGB(r, g, b));
          FastLED.show();
        }
        break;
      case 'b': //blink
        strobo();
        Serial.flush();

        break;
    }
  }

  delay(10);

}

void strobo() {
  for (int i = 0; i < 50; i++) {
    fill_solid( leds, NUM_LEDS, CRGB(255, 255, 255));
    FastLED.show();
    delay(del);
    // Now turn the LED off, then pause
    fill_solid( leds, NUM_LEDS, CRGB(0, 0, 00));
    FastLED.show();
    delay(del);
  }
}

