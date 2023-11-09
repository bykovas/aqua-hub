#include <ArduinoJson.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <BH1750.h>
#include "DFRobot_GP8403.h"
#include <SoftwareSerial.h>
#include "contracts.h"

#define ONE_WIRE_BUS 2
#define DHTPIN 3
#define DHTTYPE DHT22
#define RX_PIN 5
#define TX_PIN 6
#define RED_LED_PIN 7
#define GREEN_LED_PIN 8
#define SERIAL_BAUD_RATE 9600
#define SENSOR_READ_INTERVAL 10000
#define AIR_FAN_PIN 9
#define DAC_ADDRESS 0x5f

SoftwareSerial mySerial(RX_PIN, TX_PIN);
DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
BH1750 lightMeter;
DFRobot_GP8403 dac(&Wire, DAC_ADDRESS);

SensorData sensorData;

void setup() {
    pinMode(RED_LED_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(AIR_FAN_PIN, OUTPUT);
    Serial.begin(SERIAL_BAUD_RATE);
    mySerial.begin(SERIAL_BAUD_RATE);
    dht.begin();
    sensors.begin();
    Wire.begin();
    lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
    while (dac.begin() != 0) {
        delay(500);
    }
    dac.setDACOutRange(dac.eOutputRange10V);
    Serial.println(F("Device initialized and ready to collect data."));
}

void loop() {
    static unsigned long lastSensorReadMillis = 0;
    unsigned long currentMillis = millis();

    if (sensorData.error.length() > 0) {
        blinkRed(currentMillis);
        digitalWrite(GREEN_LED_PIN, LOW);
    }
    else {
        blinkGreen(currentMillis);
        digitalWrite(RED_LED_PIN, LOW);
    }

    if (currentMillis - lastSensorReadMillis >= SENSOR_READ_INTERVAL) {
        lastSensorReadMillis = currentMillis;
        readSensors();
        sendSensorData();
    }

    if (Serial.available()) {
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, Serial);

        if (!error) {
            JsonArray drivers = doc["drivers"];
            for (JsonObject driver : drivers) {
                const char* name = driver["name"];
                float value = driver["value"];

                if (strcmp(name, "air_fan") == 0) {
                    setAirFanSpeed(value);
                }
                else if (strcmp(name, "light_blue") == 0) {
                    setLightBlue(value);
                }
                else if (strcmp(name, "light_coral") == 0) {
                    setLightCoral(value);
                }
            }
        }
    }
}

void setAirFanSpeed(float percentage) {
    int pwmValue = map(percentage, 0, 100, 0, 255);
    analogWrite(AIR_FAN_PIN, pwmValue);
    sensorData.air_fan = percentage;
}

void setLightBlue(float percentage) {
    int value = map(percentage, 0, 100, 0, 5000);
    dac.setDACOutVoltage(value, 0);
    sensorData.light_blue = percentage;
}

void setLightCoral(float percentage) {
    int value = map(percentage, 0, 100, 0, 5000);
    dac.setDACOutVoltage(value, 1);
    sensorData.light_coral = percentage;
}

void handleIncomingData(JsonDocument& doc) {
    JsonArray drivers = doc["drivers"];
    for (JsonObject driver : drivers) {
        String name = driver["name"].as<String>();
        Serial.println(name);
        if (name == "air_fan") {
            int pwmValue = driver["value"].as<float>() / 100.0 * 255;
            analogWrite(AIR_FAN_PIN, pwmValue);
            sensorData.air_fan = driver["value"].as<float>();
        }
    }
}

void readSensors() {
    sensorData.error = "";
    sensorData.temperature_water = readWaterTemperature();
    sensorData.temperature_air = readAirTemperature();
    sensorData.humidity = readHumidity();
    sensorData.light = readLux();
}

void sendSensorData() {
    StaticJsonDocument<256> jsonDoc;
    serializeSensorDataToJson(sensorData, jsonDoc);
    if (Serial) {
        serializeJson(jsonDoc, Serial);
        Serial.println();
    }
    serializeJson(jsonDoc, mySerial);
}

void blinkRed(unsigned long currentMillis) {
    static unsigned long previousMillisRed = 0;
    static bool ledStateRed = LOW;
    const long intervalRedOn = 750;
    const long intervalRedOff = 250;

    if (sensorData.error.length() > 0) {
        if ((ledStateRed == HIGH) && (currentMillis - previousMillisRed >= intervalRedOn)) {
            ledStateRed = LOW;
            previousMillisRed = currentMillis;
        }
        else if ((ledStateRed == LOW) && (currentMillis - previousMillisRed >= intervalRedOff)) {
            ledStateRed = HIGH;
            previousMillisRed = currentMillis;
        }
        digitalWrite(RED_LED_PIN, ledStateRed);
    }
    else {
        digitalWrite(RED_LED_PIN, LOW);
    }
}

void blinkGreen(unsigned long currentMillis) {
    static unsigned long previousMillisGreen = 0;
    static bool ledStateGreen = LOW;
    const long intervalGreenOn = 100;
    const long intervalGreenOff = 900;

    if (sensorData.error.length() == 0) {
        if ((ledStateGreen == HIGH) && (currentMillis - previousMillisGreen >= intervalGreenOn)) {
            ledStateGreen = LOW;
            previousMillisGreen = currentMillis;
        }
        else if ((ledStateGreen == LOW) && (currentMillis - previousMillisGreen >= intervalGreenOff)) {
            ledStateGreen = HIGH;
            previousMillisGreen = currentMillis;
        }
        digitalWrite(GREEN_LED_PIN, ledStateGreen);
    }
    else {
        digitalWrite(GREEN_LED_PIN, LOW);
    }
}

float readWaterTemperature() {
    sensors.requestTemperatures();
    float temp = sensors.getTempCByIndex(0);
    if (temp != DEVICE_DISCONNECTED_C) {
        return temp;
    }
    sensorData.error += "Water temperature sensor disconnected; ";
    return NAN;
}

float readAirTemperature() {
    float temp = dht.readTemperature();
    if (!isnan(temp)) {
        return temp;
    }
    sensorData.error += "Air temperature sensor failed; ";
    return NAN;
}

float readHumidity() {
    float hum = dht.readHumidity();
    if (!isnan(hum)) {
        return hum;
    }
    sensorData.error += "Humidity sensor failed; ";
    return NAN;
}

float readLux() {
    float lux = lightMeter.readLightLevel();
    if (!isnan(lux) && lux >= 0) {
        return lux;
    }
    sensorData.error += "Light level sensor failed; ";
    return NAN;
}