const int SW_PIN = 50;

void setup() {
  Serial.begin(9600);
  digitalWrite(SW_PIN, HIGH);
}

void loop() {
  int xValue = analogRead(A7); // Assuming X-axis is connected to A0
  int yValue = analogRead(A6); // Assuming Y-axis is connected to A1

  Serial.print("X:");
  Serial.print(xValue);
  Serial.print(",Y:");
  Serial.print(yValue);
  Serial.print(",Switch Value:");
  Serial.println(digitalRead(SW_PIN));
  delay(100); // Adjust as needed
}