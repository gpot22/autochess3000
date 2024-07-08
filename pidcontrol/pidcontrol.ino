#define ENC1 18  // GREEN
#define ENC2 19  // YELLOW

#define MTR_EN 23 // GREEN
#define MTR_PHASE 21  // BLUE


int pos = 0;
long prevT = 0;
float eprev = 0;
float eintegral = 0;

int spd = 75;

void setup() {
  Serial.begin(19200);
  pinMode(ENC1, INPUT);
  pinMode(ENC2, INPUT);
  pinMode(MTR_PHASE, OUTPUT);
  ledcAttachPin(MTR_EN, 0);
  ledcSetup(0, 30000, 8);  // channel, freq, resolution
  attachInterrupt(digitalPinToInterrupt(ENC1), readEncoder, RISING);
}

void loop() {
  // set target position
  //int target = 250 * sin(prevT / 1e6);
  int target = 1200;
  // PID constants
  float kp = 2.2;
  float kd = 0.20;
  float ki = 0.07;

  // time difference
  long currT = micros();
  float dt = ((float)(currT - prevT)) / 1.0e6;
  prevT = currT;

  // error
  int e = target - pos; // pos-target or target-pos, depends on wiring

  // derivative
  float dedt = (e - eprev) / (dt);

  //integral
  eintegral = eintegral + e * dt;

  // control signal u(t)
  float u = kp * e + ki * eintegral + kd * dedt;

  // -- SEND SIGNAL TO MOTOR
  // motor power
  float pwr = fabs(u);
  if (pwr > 255) {
    pwr = 255;
  }

  // motor direction
  int dir = 1;
  if (u < 0) {
    dir = -1;
  }

  // signal the motor
  setMotor(dir, pwr, MTR_EN, MTR_PHASE);

  // store previous error
  eprev = e;

  Serial.print(target);
  Serial.print(" ");
  Serial.print(pos);
  Serial.println();

}

void setMotor(int dir, int pwmVal, int en, int phase) {
  ledcWrite(0, pwmVal);
  if (dir == 1) {
    digitalWrite(phase, LOW);
    Serial.println("Low");
  } else if (dir == -1) {
    digitalWrite(phase, HIGH);
    Serial.println("High");
  } else {
    ledcWrite(0, 0);
  }
}

void readEncoder() {
  int b = digitalRead(ENC2);
  if (b > 0) { // signal already high, therefore CW
    pos++;
  } else { // CCW
    pos--;
  }
}

void testCycle() {
  setMotor(1, spd, MTR_EN, MTR_PHASE);
  delay(200);
  Serial.println(pos);
  setMotor(-1, spd, MTR_EN, MTR_PHASE);
  delay(200);
  Serial.println(pos);
}
