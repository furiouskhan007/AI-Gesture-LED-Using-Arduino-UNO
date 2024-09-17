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
      if (command.startsWith("R")) {
        analogWrite(pinRed, 0);  // Full intensity Red
        analogWrite(pinGreen, 255);  // Turn off Green
        analogWrite(pinBlue, 255);  // Turn off Blue
      } else if (command.startsWith("G")) {
        analogWrite(pinRed, 255);  // Turn off Red
        analogWrite(pinGreen, 0);  // Full intensity Green
        analogWrite(pinBlue, 255);  // Turn off Blue
      } else if (command.startsWith("B")) {
        analogWrite(pinRed, 255);  // Turn off Red
        analogWrite(pinGreen, 255);  // Turn off Green
        analogWrite(pinBlue, 0);  // Full intensity Blue
      } else if (command.startsWith("P")) {
        analogWrite(pinRed, 128);  // Half intensity Red
        analogWrite(pinGreen, 255);  // Turn off Green
        analogWrite(pinBlue, 128);  // Half intensity Blue
      } else if (command.startsWith("L")) {
        analogWrite(pinRed, 255);  // Turn off Red
        analogWrite(pinGreen, 128);  // Half intensity Green
        analogWrite(pinBlue, 128);  // Half intensity Blue
      } else if (command.startsWith("Y")) {
        analogWrite(pinRed, 128);  // Half intensity Red
        analogWrite(pinGreen, 128);  // Half intensity Green
        analogWrite(pinBlue, 255);  // Turn off Blue
      } else if (command.startsWith("O")) {
        analogWrite(pinRed, 128);  // Half intensity Red
        analogWrite(pinGreen, 200);  // Low intensity Green
        analogWrite(pinBlue, 255);  // Turn off Blue
      }

      // Handle dimming commands
      if (command.startsWith("DR")) {
        int dimValue = command.substring(2).toInt();
        analogWrite(pinRed, 255 - dimValue);  // Control dimming for Red
      } else if (command.startsWith("DG")) {
        int dimValue = command.substring(2).toInt();
        analogWrite(pinGreen, 255 - dimValue);  // Control dimming for Green
      } else if (command.startsWith("DB")) {
        int dimValue = command.substring(2).toInt();
        analogWrite(pinBlue, 255 - dimValue);  // Control dimming for Blue
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
