#include <Wire.h>


int turn_percent = 0;
int target_distance = 0;
float speed_float = 0;
float maxSpeed = 2.0;

void upadate_speed(int new_turn_percent){
  float middle = (float)((turn_percent-127.0)/127.0)*maxSpeed;
  speed_float = -1*middle;
}

void receiveEvent(int howMany) {
  if (Wire.available()>=2){
    turn_percent = Wire.read();
    target_distance = Wire.read();
  }

  //if there is extra
  while(Wire.available()) {
     Wire.read();
  }
  upadate_speed(turn_percent);
      
}



int i2c_handler_start(){

}

void setup() {
  Wire.begin(0x8);                // join i2c bus with address #8
  Wire.onReceive(receiveEvent); // register event
  Serial.begin(9600);
  i2c_handler_start();
}

void loop(){ 
  delay(100);
  Serial.print("Turn percent = ");
  Serial.print(turn_percent);
  Serial.print(" Turn speed = ");
  Serial.println(speed_float);
}


