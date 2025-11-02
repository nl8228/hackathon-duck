int speakerPin = 9;
int analogPin = A0;  // Connect Pi GPIO here

const int threshold = 600; // Analog value threshold to consider "HIGH"
const int stableDelay = 10;  // ms between readings
const int stableCount = 5;   // number of consecutive readings above threshold

// Returns true if analog value is stably above threshold
bool isStablyHigh() {
  int count = 0;
  for (int i = 0; i < stableCount; i++) {
    int val = analogRead(analogPin);
    if (val >= threshold) {
      count++;
    } else {
      count = 0; // reset if below threshold
    }
    delay(stableDelay);
  }
  return count == stableCount;
}

void setup() {
  pinMode(speakerPin, OUTPUT);
}

void loop() {
  // Only play sweep if analog pin is stably "HIGH"
  if (isStablyHigh()) {

    // Sweep up 200 Hz → 1000 Hz
    for (int freq = 200; freq <= 1000; freq += 5) {
      if (analogRead(analogPin) < threshold) { // stop if voltage drops
        noTone(speakerPin);
        return;
      }
      tone(speakerPin, freq);
      delay(10);
    }

    // Sweep down 1000 Hz → 200 Hz
    for (int freq = 1000; freq >= 200; freq -= 5) {
      if (analogRead(analogPin) < threshold) { // stop if voltage drops
        noTone(speakerPin);
        return;
      }
      tone(speakerPin, freq);
      delay(10);
    }

  } else {
    noTone(speakerPin); // pin not stably HIGH
  }
}
