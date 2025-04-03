#include <Arduino.h>
#include <Stepper.h>

// # steps for full 360-degree rotation, change to fit your motor
int stepsPerRevolution = 2048;
int setStepDegrees = 10;
int moveDegrees = 2048 / 360 * setStepDegrees;
bool xDirectionFlag = true;
bool yDirectionFlag = true;
int xStepCounter = 0;
int yStepCounter = 0;
int xDeg = 0;
int yDeg = 0;
// set a speed for the stepper motor
int rpm = 9;

// initialize stepper library on pins 8 - 11
// pin order IN1, IN3, IN2, IN4
Stepper xAxisMotor (stepsPerRevolution, 8, 10, 9, 11);
Stepper yAxisMotor (stepsPerRevolution, 2, 3, 4, 5);

void setup() {
  Serial.begin(9600);
  xAxisMotor.setSpeed(rpm);
  yAxisMotor.setSpeed(rpm);
}

void printPos() {
  xDeg = (xDirectionFlag) ? (10 * xStepCounter) : 120 - (10 * xStepCounter);
  Serial.print("xPosDeg: ");
  Serial.print(xDeg);

  yDeg = (yDirectionFlag) ? (10 * yStepCounter) : 60 - (10 * yStepCounter);
  Serial.print("\tyPosDeg: ");
  Serial.println(yDeg);
}

bool isXSweepDone() { return (xStepCounter >= 12) ? true : false; }

bool isYSweepDone() { return (yStepCounter >= 6) ? true : false; }

bool xMotorControl() {
  if (!isXSweepDone()) {
    if (xDirectionFlag) {
      xAxisMotor.step(moveDegrees);
      delay(100);
    }
  
    if (!xDirectionFlag) {
      xAxisMotor.step(-moveDegrees);
      delay(100);
    }
  }
  else { 
    xStepCounter = 0;
    xDirectionFlag = !xDirectionFlag;
    return false;
  }
  xStepCounter++;
  return true;
}

bool yMotorControl() {
  if (!isYSweepDone()) {
    if (yDirectionFlag) {
      yAxisMotor.step(moveDegrees);
    }
    else if (!yDirectionFlag) {
      yAxisMotor.step(-moveDegrees);
    }
  }
  else { 
    yStepCounter = 0;
    yDirectionFlag = !yDirectionFlag;
    return false;
  }
  yStepCounter++;
  return true;
}

void loop() {
  if (Serial.available() > 0) {
    // Read incoming data
    String incomingData = Serial.readString();  // Read the incoming data as a string

    //is xdoes not move then move y
    if (!xMotorControl()) {
      yMotorControl();  
    }

    delay(100);
    printPos();
  }

 
}