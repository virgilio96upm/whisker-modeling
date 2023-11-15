#include <Tlv493d.h>
#include <Wire.h>

// Tlv493d Opject
Tlv493d Tlv493dMagnetic3DSensor = Tlv493d();

void setup() {
  Wire.begin();

  Serial.begin(9600);
  while(!Serial);
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
  delay(Tlv493dMagnetic3DSensor.getMeasurementDelay()*2);
  Wire.beginTransmission(0x72);
  Wire.write(2);
  Wire.endTransmission();
  Tlv493dMagnetic3DSensor.updateData();
  Serial.print("x_1:");
  Serial.print(Tlv493dMagnetic3DSensor.getX());
  Serial.print(",");
  Serial.print("Y_1:");
  Serial.print(Tlv493dMagnetic3DSensor.getY());
  Serial.print(",");
  Serial.print("z_1:");
  Serial.println(Tlv493dMagnetic3DSensor.getZ());

  /*Serial.print(",");
  Wire.beginTransmission(0x70);
  Wire.write(0x02);
  Wire.endTransmission();
  Tlv493dMagnetic3DSensor.updateData();
  Serial.print("X_2:");
  Serial.print(Tlv493dMagnetic3DSensor.getX());
  Serial.print(",");
  Serial.print("Y_2:");
  Serial.print(Tlv493dMagnetic3DSensor.getY());
  Serial.print(",");
  Serial.print("Z_2:");  
  Serial.println(Tlv493dMagnetic3DSensor.getZ());
*/
}

