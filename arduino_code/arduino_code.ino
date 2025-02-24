#include <SoftwareSerial.h>

// Define Bluetooth module connections
SoftwareSerial Bluetooth(10, 11); // RX, TX

// Motor control pins
#define ENA 9
#define ENB 3
#define IN1 8
#define IN2 7
#define IN3 5
#define IN4 4

// Ultrasonic sensor pins
#define TRIG 13
#define ECHO 12

void setup() {
    Serial.begin(9600);       // Serial for debugging
    Bluetooth.begin(9600);    // Bluetooth communication
    
    // Set motor pins as output
    pinMode(ENA, OUTPUT);
    pinMode(ENB, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);

    // Set ultrasonic sensor pins
    pinMode(TRIG, OUTPUT);
    pinMode(ECHO, INPUT);

    Serial.println("Arduino Ready. Waiting for commands...");
}

// Function to measure distance using the ultrasonic sensor
int getDistance() {
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);
    
    long duration = pulseIn(ECHO, HIGH);
    int distance = duration * 0.034 / 2;
    return distance;
}

// Function to move forward
void moveForward() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 160);
    analogWrite(ENB, 160);
}

// Function to move backward
void moveBackward() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENA, 150);
    analogWrite(ENB, 150);
}

// Function to turn left
void turnLeft() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 130);
    analogWrite(ENB, 130);
}

// Function to turn right
void turnRight() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENA, 130);
    analogWrite(ENB, 130);
}

// Function to stop
void stopMotors() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
}

// Function to execute movement commands
void executeCommand(String command) {
    if (command == "forward") {
        moveForward();
        delay(700);
        stopMotors();
    } else if (command == "backward") {
        moveBackward();
        delay(500);
        stopMotors();
    } else if (command == "turn_left") {
        turnLeft();
        delay(570);
        stopMotors();
    } else if (command == "turn_right") {
        turnRight();
        delay(570);
        stopMotors();
    } /*else if (command == "turn_back") {
        turnRight();
        delay(500);
        stopMotors();
    }*/
}

void loop() {
    // Send distance to Raspberry Pi
    int distance = getDistance();
    Bluetooth.print("Distance:");
    Bluetooth.println(distance);
    delay(500);

    // Receive and execute commands from Raspberry Pi
    if (Bluetooth.available()) {
        String command = Bluetooth.readStringUntil('\n');
        command.trim();
        Serial.println("Received command: " + command);
        executeCommand(command);
    }
}
