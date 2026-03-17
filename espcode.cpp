#include <Arduino.h>
#include <ESP32Servo.h>

// ---------------- CONFIG ----------------
#define MIN_SPEED 255 
#define MAX_SPEED 255
#define DEBUG_LED 2

// ---------------- PINS (MOTORS) ----------------
const int STBY = 33;
const int PWMA = 13;
const int AIN1 = 12;
const int AIN2 = 14;
const int PWMB = 27;
const int BIN1 = 26;
const int BIN2 = 25;

// ---------------- PINS (EARS) ----------------
const int servo1Pin = 22; // Left Ear
const int servo2Pin = 23; // Right Ear

// ---------------- EAR SETTINGS ----------------
const int EAR_BACK = 20;
const int EAR_NEUTRAL = 90;
const int EAR_FORWARD = 160;
const int EAR_DROOP = 60;

Servo servo1;
Servo servo2;

int currentLeft = 90;
int currentRight = 90;
unsigned long lastEarUpdate = 0;
unsigned long nextEarEventTime = 0;
bool isMovingMotors = false;

// ---------------- MOTOR HELPERS ----------------
void setMotorPWM(int pin, int val) {
  #if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcWrite(pin, val);
  #else
    if (pin == PWMA) ledcWrite(0, val);
    if (pin == PWMB) ledcWrite(1, val);
  #endif
}

void initPWM(int pin, int channel) {
  #if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcAttach(pin, 1000, 8);
  #else
    ledcSetup(channel, 1000, 8);
    ledcAttachPin(pin, channel);
  #endif
}

void stopMotors() {
  digitalWrite(AIN1, LOW); digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW); digitalWrite(BIN2, LOW);
  setMotorPWM(PWMA, 0); setMotorPWM(PWMB, 0);
  isMovingMotors = false;
}

void moveRaw(int speed, bool a_fwd, bool b_fwd) {
  digitalWrite(AIN1, a_fwd ? HIGH : LOW);
  digitalWrite(AIN2, a_fwd ? LOW : HIGH);
  setMotorPWM(PWMA, speed);

  digitalWrite(BIN1, b_fwd ? HIGH : LOW);
  digitalWrite(BIN2, b_fwd ? LOW : HIGH);
  setMotorPWM(PWMB, speed);
  isMovingMotors = true;
}

// ---------------- EAR HELPERS ----------------
// Smoothly move servos without blocking code
void updateEars(int targetLeft, int targetRight, int speed) {
  if (currentLeft < targetLeft) currentLeft += speed;
  if (currentLeft > targetLeft) currentLeft -= speed;
  if (currentRight < targetRight) currentRight += speed;
  if (currentRight > targetRight) currentRight -= speed;

  servo1.write(currentLeft);
  servo2.write(currentRight);
}

// Instant ear pose
void setEars(int left, int right) {
  currentLeft = left;
  currentRight = right;
  servo1.write(left);
  servo2.write(right);
}

// ---------------- SETUP ----------------
void setup() {
  Serial.begin(115200);
  pinMode(DEBUG_LED, OUTPUT);
  randomSeed(analogRead(0));

  // Flash LED
  for(int i=0; i<3; i++) {
    digitalWrite(DEBUG_LED, HIGH); delay(100);
    digitalWrite(DEBUG_LED, LOW); delay(100);
  }

  // Motor Setup
  pinMode(STBY, OUTPUT);
  pinMode(AIN1, OUTPUT); pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT); pinMode(BIN2, OUTPUT);
  initPWM(PWMA, 0);
  initPWM(PWMB, 1);
  digitalWrite(STBY, HIGH);

  // Servo Setup
  servo1.attach(servo1Pin, 500, 2400);
  servo2.attach(servo2Pin, 500, 2400);
  setEars(EAR_NEUTRAL, EAR_NEUTRAL);

  Serial.println("READY_CAT_MODE");
}

// ---------------- LOOP ----------------
void loop() {
  unsigned long currentMillis = millis();

  // 1. READ COMMANDS
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() > 0) {
      digitalWrite(DEBUG_LED, !digitalRead(DEBUG_LED)); // Flash debug
      Serial.print("ACK:"); Serial.println(cmd);

      // --- MOTOR COMMANDS ---
// ... inside void loop() ...

      // --- MOTOR COMMANDS ---
      if (cmd == "forward") {
        setEars(EAR_FORWARD, EAR_FORWARD);
        moveRaw(MIN_SPEED, true, true);
        delay(5000); // Increased to 1 second for better movement
        stopMotors();
        Serial.println("DONE"); // <--- CRITICAL ADDITION
      }
      else if (cmd == "back") {
        setEars(EAR_BACK, EAR_BACK);
        moveRaw(MIN_SPEED, false, false);
        delay(5000); 
        stopMotors();
        Serial.println("DONE"); // <--- CRITICAL ADDITION
      }
      else if (cmd == "left") {
        setEars(EAR_BACK, EAR_FORWARD);
        moveRaw(MIN_SPEED, false, true);
        delay(5000); 
        stopMotors();
        Serial.println("DONE"); // <--- CRITICAL ADDITION
      }
      else if (cmd == "right") {
        setEars(EAR_FORWARD, EAR_BACK);
        moveRaw(MIN_SPEED, true, false);
        delay(5000); 
        stopMotors();
        Serial.println("DONE"); // <--- CRITICAL ADDITION
      }
      else if (cmd == "stop") {
        stopMotors();
        setEars(EAR_NEUTRAL, EAR_NEUTRAL);
      }
      // Reset ear timer so it doesn't interrupt movement immediately
      nextEarEventTime = currentMillis + 2000; 
    }
  }

  // 2. IDLE CAT BEHAVIOR (Only if motors are stopped)
  if (!isMovingMotors && currentMillis > nextEarEventTime) {
    int behavior = random(100);

    // Pick a random ear action
    if (behavior < 30) { 
      // Twitch
      int ear = random(2);
      if(ear==0) servo1.write(EAR_FORWARD+10); else servo2.write(EAR_FORWARD+10);
      delay(80);
      servo1.write(currentLeft); servo2.write(currentRight);
      nextEarEventTime = currentMillis + random(1000, 3000);
    }
    else if (behavior < 50) {
      // Alert Scan
      updateEars(EAR_FORWARD, EAR_FORWARD, 5);
      nextEarEventTime = currentMillis + random(2000, 4000);
    }
    else if (behavior < 70) {
      // Curious (One ear up)
      if (random(2) == 0) setEars(EAR_FORWARD, EAR_NEUTRAL);
      else setEars(EAR_NEUTRAL, EAR_FORWARD);
      nextEarEventTime = currentMillis + random(1500, 3000);
    }
    else if (behavior < 85) {
      // Sleepy / Droop
      updateEars(EAR_DROOP, EAR_DROOP, 2);
      nextEarEventTime = currentMillis + random(4000, 6000);
    }
    else {
      // Wiggle / Reset
      setEars(EAR_NEUTRAL, EAR_NEUTRAL);
      nextEarEventTime = currentMillis + random(2000, 5000);
    }
  }
}
