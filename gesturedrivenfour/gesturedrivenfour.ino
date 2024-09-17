// Arduino Code
const int pinRed = 6;
const int pinGreen = 5;
const int pinBlue = 3;

void setup() {
  pinMode(pinRed, OUTPUT);
  pinMode(pinGreen, OUTPUT);
  pinMode(pinBlue, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  static String command = "";
  
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      // Process the complete command
      if (command.startsWith("P")) {
        // Purple (combination of Red and Blue)
        analogWrite(pinRed, 128);  // Half intensity Red
        analogWrite(pinGreen, 255);  // Off Green
        analogWrite(pinBlue, 128);  // Half intensity Blue
      } else if (command.startsWith("L")) {
        // Light Blue (combination of Green and Blue)
        analogWrite(pinRed, 255);  // Off Red
        analogWrite(pinGreen, 128);  // Half intensity Green
        analogWrite(pinBlue, 128);  // Half intensity Blue
      } else if (command.startsWith("Y")) {
        // Yellow (combination of Red and Green)
        analogWrite(pinRed, 128);  // Half intensity Red
        analogWrite(pinGreen, 128);  // Half intensity Green
        analogWrite(pinBlue, 255);  // Off Blue
      } else if (command.startsWith("O")) {
        // Orange (mostly Red with a bit of Green)
        analogWrite(pinRed, 128);  // Half intensity Red
        analogWrite(pinGreen, 200);  // Low intensity Green
        analogWrite(pinBlue, 255);  // Off Blue
      }

      // Handle dimming commands with inverted logic for these colors
      if (command.startsWith("DP")) {
        int dimValue = command.substring(2).toInt();
        int invertedDim = 255 - dimValue;  // Invert dimming logic
        // Adjust dimming for Purple (Red and Blue)
        analogWrite(pinRed, invertedDim);  
        analogWrite(pinBlue, invertedDim);
      } else if (command.startsWith("DL")) {
        int dimValue = command.substring(2).toInt();
        int invertedDim = 255 - dimValue;  // Invert dimming logic
        // Adjust dimming for Light Blue (Green and Blue)
        analogWrite(pinGreen, invertedDim);  
        analogWrite(pinBlue, invertedDim);
      } else if (command.startsWith("DY")) {
        int dimValue = command.substring(2).toInt();
        int invertedDim = 255 - dimValue;  // Invert dimming logic
        // Adjust dimming for Yellow (Red and Green)
        analogWrite(pinRed, invertedDim);  
        analogWrite(pinGreen, invertedDim);
      } else if (command.startsWith("DO")) {
        int dimValue = command.substring(2).toInt();
        int invertedDim = 255 - dimValue;  // Invert dimming logic
        // Adjust dimming for Orange (Red and Green)
        analogWrite(pinRed, invertedDim);  
        analogWrite(pinGreen, invertedDim);
      }

      command = "";  // Clear command buffer
    } else {
      command += c;  // Accumulate the command
    }
  }
}
