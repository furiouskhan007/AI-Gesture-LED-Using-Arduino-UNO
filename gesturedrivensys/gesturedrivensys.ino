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
        analogWrite(pinRed, 0);  // Turn on Red
        analogWrite(pinGreen, 255);  // Turn off Green
        analogWrite(pinBlue, 255);  // Turn off Blue
      } else if (command.startsWith("G")) {
        analogWrite(pinRed, 255);  // Turn off Red
        analogWrite(pinGreen, 0);  // Turn on Green
        analogWrite(pinBlue, 255);  // Turn off Blue
      } else if (command.startsWith("B")) {
        analogWrite(pinRed, 255);  // Turn off Red
        analogWrite(pinGreen, 255);  // Turn off Green
        analogWrite(pinBlue, 0);  // Turn on Blue
      } else if (command.startsWith("DR")) {
        int dimValue = command.substring(2).toInt();
        analogWrite(pinRed, 255 - dimValue);  // Control dimming for Red
      } else if (command.startsWith("DG")) {
        int dimValue = command.substring(2).toInt();
        analogWrite(pinGreen, 255 - dimValue);  // Control dimming for Green
      } else if (command.startsWith("DB")) {
        int dimValue = command.substring(2).toInt();
        analogWrite(pinBlue, 255 - dimValue);  // Control dimming for Blue
      }

      command = "";  // Clear command buffer
    } else {
      command += c;  // Accumulate the command
    }
  }
}
