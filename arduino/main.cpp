#include <Arduino.h>
#include "MPU9250.h"
#include <Wire.h>
#include <string.h>

#define SLAVE_ADDRESS 0x04

MPU9250 IMU(SPI, 10);
int status, val;
char accel[20], gyro[20], mag[20], temp[20];

void receiveData(int byteCount) 
{
    while(Wire.available() > 0) 
    {
        val = Wire.read();
        Serial.println(val);
    }
}

void sendData() 
{
    switch (val) 
    {
        case 65:
                Wire.write(accel);
                break;
        case 71:
                Wire.write(gyro);
                break;
        case 77:
                Wire.write(mag);
                break;
        case 84:
                Wire.write(temp);
                break;
    }
}

// This is the first function which will be call by the Arduino.h library...
void setup() {
    // Start serial (USB - communication to the PC)...      (Only for debugging)
    Serial.begin(115200);
    Serial.println("Start!");
    while(!Serial) {}
    
    // Connect to the MPU9250 9-axis sensor...
    status = IMU.begin();
    if (status < 0) {
            Serial.println("IMU initialization unsuccessful");
            Serial.println("Check IMU wiring or try cycling power");
            Serial.print("Status: ");
            Serial.println(status);
            while(1) {}
    }
    
    // Start the I2C communication to the ev3...
    Wire.begin(SLAVE_ADDRESS);
    Wire.onReceive(receiveData);
    Wire.onRequest(sendData);
}

// Loop is the main programm and runs endlessly (This function will be call after the setup fuction by the Arduin.h library)...
void loop() {
    // Update the sensor data...
    IMU.readSensor();

    float value1,value2, value3;
    char array1[6], array2[6], array3[6];

    // Get accel data...
    value1 = IMU.getAccelX_mss();
    value2 = IMU.getAccelY_mss();
    value3 = IMU.getAccelZ_mss();
    // Convert the floats to a char array...
    String(value1).toCharArray(array1, 6);
    String(value2).toCharArray(array2, 6);
    String(value3).toCharArray(array3, 6);
    // Connect the char arrays to one array...
    sprintf(accel, "%s:%s:%s", array1, array2, array3);

    // Get gyro data...
    value1 = IMU.getGyroX_rads();
    value2 = IMU.getGyroY_rads();
    value3 = IMU.getGyroZ_rads();
    // Convert the floats to a char array...
    String(value1).toCharArray(array1, 6);
    String(value2).toCharArray(array2, 6);
    String(value3).toCharArray(array3, 6);
    // Connect the char arrays to one array...
    sprintf(gyro, "%s:%s:%s", array1, array2, array3);

    // Get mag data...
    value1 = IMU.getMagX_uT();
    value2 = IMU.getMagY_uT();
    value3 = IMU.getMagZ_uT();
    // Convert the floats to a char array...
    String(value1).toCharArray(array1, 6);
    String(value2).toCharArray(array2, 6);
    String(value3).toCharArray(array3, 6);
    // Connect the char arrays to one array...
    sprintf(mag, "%s:%s:%s", array1, array2, array3);

    // Get temp data...
    value1 = IMU.getTemperature_C();
    value2 = 0.0;
    value3 = 0.0;
    // Convert the floats to a char array...
    String(value1).toCharArray(array1, 6);
    String(value2).toCharArray(array2, 6);
    String(value3).toCharArray(array3, 6);
    // Connect the char arrays to one array...
    sprintf(temp, "%s:%s:%s", array1, array2, array3);    

    // Wait 100 ms...
    delay(100);
}
