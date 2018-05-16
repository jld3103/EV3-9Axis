#include <Arduino.h>
#include "MPU9250.h"
#include <Wire.h>

#define SLAVE_ADDRESS 0x0

MPU9250 IMU(SPI, 10);
int status, val;
void receiveData(int byteCount) {
        while(Wire.available() > 0) {
                val = Wire.read();
        }
}

void sendData() {
        float send;

        IMU.readSensor();

        switch (val) {
        case 0:
                send = IMU.getAccelX_mss();
                break;
        case 1:
                send = IMU.getAccelY_mss();
                break;
        case 2:
                send = IMU.getAccelZ_mss();
                break;
        case 3:
                send = IMU.getGyroX_rads();
                break;
        case 4:
                send = IMU.getGyroY_rads();
                break;
        case 5:
                send = IMU.getGyroZ_rads();
                break;
        case 6:
                send = IMU.getMagX_uT();
                break;
        case 7:
                send = IMU.getMagY_uT();
                break;
        case 8:
                send = IMU.getMagZ_uT();
                break;
        case 9:
                send = IMU.getTemperature_C();
                break;
        }
}

void setup() {
        Serial.begin(115200);
        while(!Serial) {}

        status = IMU.begin();
        if (status < 0) {
                Serial.println("IMU initialization unsuccessful");
                Serial.println("Check IMU wiring or try cycling power");
                Serial.print("Status: ");
                Serial.println(status);
                while(1) {}
        }
        Wire.begin(SLAVE_ADDRESS);
        Wire.onReceive(receiveData);
        Wire.onRequest(sendData);
}

void loop() {
}
