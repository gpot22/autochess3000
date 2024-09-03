#define MOTOR0_EN 25
#define MOTOR0_PHASE 26
#define MOTOR0_ENC1 22
#define MOTOR0_ENC2 23

#define MOTOR1_EN 32
#define MOTOR1_PHASE 33
#define MOTOR1_ENC1 17
#define MOTOR1_ENC2 16

#include <cmath>
const int square_size_mm = 50;  // mm

int restingCounter = 0;


class SimplePID {
  private:
    float kp, kd, ki, umax;  // Parameters
    float eprev, eintegral;  // Storage

  public:
  // Constructor
  SimplePID()
    : kp(1), kd(0), ki(0), umax(255), eprev(0.0), eintegral(0.0) {}

  // A function to set the parameters
  void setParams(float kpIn, float kdIn, float kiIn, float umaxIn) {
    kp = kpIn;
    kd = kdIn;
    ki = kiIn;
    umax = umaxIn;
  }

  // A function to compute the control signal
  void evalu(int value, int target, float deltaT, int &pwr, int &dir) {
    // error
    int e = target - value;

    // derivative
    float dedt = (e - eprev) / (deltaT);

    // integral
    eintegral = eintegral + e * deltaT;

    // control signal
    float u = kp * e + kd * dedt + ki * eintegral;

    // motor power
    pwr = (int)fabs(u);
    if (pwr > umax) {
      pwr = umax;
    }

    // motor direction
    dir = 1;
    if (u < 0) {
      dir = -1;
    }

    // store previous error
    eprev = e;
  }
};

const int num_motors = 2;

const int enca[] = { 22, 16 };
const int encb[] = { 23, 17 };
const int phase[] = { 26, 33 };
const int en[] = { 25, 32 };

long prevT = 0;
volatile int posi[] = { 0, 0 };

int target[num_motors];

SimplePID pid[num_motors];

String instructions = "";

int spd = 193;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  for (int i = 0; i < num_motors; i++) {
    pinMode(enca[i], INPUT);
    pinMode(encb[i], INPUT);
    pinMode(phase[i], OUTPUT);
    ledcAttachPin(en[i], i);
    ledcSetup(i, 30000, 8);
  }
  pid[0].setParams(1, 0, 0, 255);
  pid[1].setParams(1, 0, 0, 255);

  attachInterrupt(digitalPinToInterrupt(enca[0]), readEncoder<0>, RISING);
  attachInterrupt(digitalPinToInterrupt(enca[1]), readEncoder<1>, RISING);

  int distPulses;
  int anglePulses;
  square_to_square("a1", "c5", 0, distPulses, anglePulses);
  instructions += String("turn") + String(anglePulses) + String(",go") + String(distPulses) + String(",turn") + String(-anglePulses);

  square_to_square("c5", "h2", 0, distPulses, anglePulses);
  instructions += String(",turn") + String(anglePulses) + String(",go") + String(distPulses) + String(",turn") + String(-anglePulses);
  // Serial.println(instructions);
  // Serial.println(anglePulses);
  // turn(anglePulses, target);
}

void loop() {
  // target positions
  // int target[num_motors] = { 1232 / 2, -1232 / 2 };
  String instruction;
  if(instructions.length() > 0 && isResting()) {
    if (instructions.indexOf(",") > 0) {
      instruction = instructions.substring(0, instructions.indexOf(","));
      instructions = instructions.substring(instructions.indexOf(",")+1, instructions.length());
    } else {
      instruction = instructions;
      instructions = "";
    }
    executeInstruction(instruction);
  }

  updateMotorWithPID(target);
}

void setMotor(int dir, int pwmVal, int phase, int en_channel) {
  ledcWrite(en_channel, pwmVal);
  if (dir == 1) {
    digitalWrite(phase, LOW);
    // Serial.println("Low");
  } else if (dir == -1) {
    digitalWrite(phase, HIGH);
    // Serial.println("High");
  } else {
    ledcWrite(en_channel, 0);
  }
}

template<int j>
void readEncoder() {
  int b = digitalRead(encb[j]);
  if (b > 0) {  // signal already high, therefore CW
    posi[j]++;
  } else {  // CCW
    posi[j]--;
  }
}

void updateMotorWithPID(int*target) {
  // delta t
  long currT = micros();
  float dt = ((float)(currT - prevT)) / 1.0e6;
  prevT = currT;

  // read position
  int pos[num_motors];
  noInterrupts();  // disable interrupts temporarily while reading
  for (int k = 0; k < num_motors; k++) {
    pos[k] = posi[k];
  }
  interrupts();  // turn interrupts back on

  // loop through motors
  for (int k = 0; k < num_motors; k++) {
    int pwr, dir;
    // evaluate the control signal
    pid[k].evalu(pos[k], target[k], dt, pwr, dir);
    // signal the motor
    setMotor(dir, pwr, phase[k], k);
    
    int pwr_thresh = 30;
    if (pwr < pwr_thresh) {
      restingCounter++;
      if (restingCounter > 50) {
        restingCounter = 50;
      }
    } else {
      restingCounter = 0;
    }
  }
  displayPIDData(target, pos);
}

void displayPIDData(int*target, int*pos) {
  for (int k = 0; k < num_motors; k++) {
    Serial.print(target[k]);
    Serial.print(" ");
    Serial.print(pos[k]);
    Serial.print(" ");
  }
  Serial.println();
}

void testCycle() {
}


void square_to_square(String start, String end, int startDegrees, int &distPulses, int &anglePulses) {
  // ex: a4 to e7
  int xDist = square_size_mm * (end.charAt(0) - start.charAt(0));
  int yDist = square_size_mm * (end.charAt(1) - start.charAt(1));
  // Serial.println(xDist);
  // Serial.println(yDist);
  double dist = sqrt(xDist * xDist + yDist * yDist);
  double degrees = atan((double)yDist / xDist) * 180.0 / PI - (double)startDegrees;

  // Serial.println(dist);
  // Serial.println("!@&#^&!@#");
  distPulses = mm_to_pulses(dist);
  anglePulses = degrees_to_pulses(degrees);
  // return String(mm_to_pulses(dist)) + "," + String(degrees_to_pulses(degrees));
}

int degrees_to_pulses(double degrees) {
  return round(degrees / 90 * 1232);
}

int mm_to_pulses(double dist) {  // wheel dia = 21mm, 1 rot = 1056
  return round(dist / (21*PI) * 1056);
}

void resetPosi() {
  posi[0] = 0;
  posi[1] = 0;
}

void move(int distPulses, int * target) {
  target[0] = distPulses;
  target[1] = distPulses;
  resetPosi();
}

void turn(int anglePulses, int * target) {
  target[0] = -anglePulses;
  target[1] = anglePulses;
  resetPosi();
}

bool isResting() {
  return restingCounter >= 50;
}

void executeInstruction(String instruction) {
  // Serial.println("aaaaaaa");
  // Serial.println(instruction);
  int val;
  if(instruction.startsWith("turn")) {
    val = instruction.substring(4, instruction.length()).toInt();
    turn(val, target);
  } else if (instruction.startsWith("go")) {
    val = instruction.substring(2, instruction.length()).toInt();
    move(val, target);
  }
}

//"turn"

