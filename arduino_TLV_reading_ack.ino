#include <Tlv493d.h>
#include <Wire.h>

// Tlv493d Opject
Tlv493d Tlv493dMagnetic3DSensor = Tlv493d();

void setup() {
  Wire.begin();

  Serial.begin(9600);
  while (!Serial)
    ;
  Tlv493dMagnetic3DSensor.begin();
  Tlv493dMagnetic3DSensor.setAccessMode(Tlv493dMagnetic3DSensor.MASTERCONTROLLEDMODE);
  Tlv493dMagnetic3DSensor.disableTemp();

  Wire.beginTransmission(0x70);
  Wire.write(0x00);
  Wire.endTransmission();
  Wire.beginTransmission(0x71);
  Wire.write(0x00);
  Wire.endTransmission();
  Wire.beginTransmission(0x72);
  Wire.write(0x00);
  Wire.endTransmission();
  Wire.beginTransmission(0x73);
  Wire.write(0x00);
  Wire.endTransmission();
}

void loop() {
  delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
  Wire.beginTransmission(0x72);
  Wire.write(2);
  Wire.endTransmission();

  float bx = Tlv493dMagnetic3DSensor.getX();
  float by = Tlv493dMagnetic3DSensor.getY();
  float bz = Tlv493dMagnetic3DSensor.getZ();
  // Check for reading flag from python
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == 'R') {
      float sumBX = 0.0;
      float sumBY = 0.0;
      float sumBZ = 0.0;

      for (int i = 0; i < 64; i++) {
        delay(Tlv493dMagnetic3DSensor.getMeasurementDelay());
        Tlv493dMagnetic3DSensor.updateData();
        sumBX += Tlv493dMagnetic3DSensor.getX();
        sumBY += Tlv493dMagnetic3DSensor.getY();
        sumBZ += Tlv493dMagnetic3DSensor.getZ();
      }

      float avgBX = sumBX / 64.0;
      float avgBY = sumBY / 64.0;
      float avgBZ = sumBZ / 64.0;

      Serial.print(avgBX);
      Serial.print(",");
      Serial.print(avgBY);
      Serial.print(",");
      Serial.println(avgBZ);
    }
  }
}
