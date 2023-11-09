#include <ArduinoJson.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <BH1750.h>
#include <SoftwareSerial.h>
#include "Contracts.h" // Include the data contract definitions

// Constants and settings
#define ONE_WIRE_BUS 2
#define DHTPIN 3
#define DHTTYPE DHT22
#define RX_PIN 5
#define TX_PIN 6
#define RED_LED_PIN 7
#define GREEN_LED_PIN 8
#define SERIAL_BAUD_RATE 9600
#define RETRY_COUNT 3
#define DELAY_TIME 1000

// Sensor ranges
const float TEMP_WATER_MIN = 0.0;
const float TEMP_WATER_MAX = 50.0;
const float TEMP_AIR_MIN = 10.0;
const float TEMP_AIR_MAX = 40.0;
const float HUMIDITY_MIN = 0.0;
const float HUMIDITY_MAX = 100.0;
const float LUX_MIN = 0.0;
const float LUX_MAX = 20000.0;

// Objects for communication
SoftwareSerial mySerial(RX_PIN, TX_PIN);
DHT dht(DHTPIN, DHTTYPE);
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
BH1750 lightMeter;

// Instantiate a SensorData structure
SensorData sensorData;

// LED blinking function
void blinkLed(int pin, int delayShort, int delayLong, int countShort, int countLong) {
    for (int i = 0; i < countShort; i++) {
        digitalWrite(pin, HIGH);
        delay(delayShort);
        digitalWrite(pin, LOW);
        delay(delayShort);
    }
    for (int i = 0; i < countLong; i++) {
        digitalWrite(pin, HIGH);
        delay(delayLong);
        digitalWrite(pin, LOW);
        delay(delayLong);
    }
}

void setup() {
    pinMode(RED_LED_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    Serial.begin(SERIAL_BAUD_RATE);
    mySerial.begin(SERIAL_BAUD_RATE);
    dht.begin();
    sensors.begin();
    Wire.begin();
    lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
    Serial.println("Device initialized and ready to collect data...");
}

// Read functions
float readWaterTemperature() {
    sensors.requestTemperatures();
    float temp = sensors.getTempCByIndex(0);
    if (temp != DEVICE_DISCONNECTED_C && temp >= TEMP_WATER_MIN && temp <= TEMP_WATER_MAX) {
        return temp;
    }
    return DEVICE_DISCONNECTED_C; // Return error value
}

float readAirTemperature() {
    float temp = dht.readTemperature();
    if (!isnan(temp) && temp >= TEMP_AIR_MIN && temp <= TEMP_AIR_MAX) {
        return temp;
    }
    return NAN; // Return NaN to indicate an error
}

float readHumidity() {
    float hum = dht.readHumidity();
    if (!isnan(hum) && hum >= HUMIDITY_MIN && hum <= HUMIDITY_MAX) {
        return hum;
    }
    return NAN; // Return NaN to indicate an error
}

float readLux() {
    float lux = lightMeter.readLightLevel();
    if (isnan(lux) || lux < 0) {  // Additional check for NAN if the library supports it.
        return NAN; // Return NaN to indicate an error
    }
    return lux;
}

void loop() {
    // Reset the error message at the start of each loop iteration
    sensorData.error = "";

    // Read sensor data and accumulate errors
    sensorData.temperature_water = readWaterTemperature();
    if (sensorData.temperature_water == DEVICE_DISCONNECTED_C) {
        sensorData.error += "Water temperature sensor disconnected; ";
    }

    sensorData.temperature_air = readAirTemperature();
    if (isnan(sensorData.temperature_air)) {
        sensorData.error += "Air temperature sensor failed; ";
    }

    sensorData.humidity = readHumidity();
    if (isnan(sensorData.humidity)) {
        sensorData.error += "Humidity sensor failed; ";
    }

    sensorData.light = readLux();
    if (isnan(sensorData.light)) {
        sensorData.error += "Light level sensor failed; ";
    }

    // Create a JSON document
    StaticJsonDocument<256> jsonDoc;
    serializeSensorDataToJson(sensorData, jsonDoc);

    // Blink LEDs based on errors or Serial availability
    if (!sensorData.error.isEmpty() || !Serial) {
        digitalWrite(GREEN_LED_PIN, LOW);
        blinkLed(RED_LED_PIN, 250, 750, 3, 3);
    }
    else {
        digitalWrite(RED_LED_PIN, LOW);
        blinkLed(GREEN_LED_PIN, 250, 0, 1, 0);
    }

    // Print JSON to Serial for debugging
    if (Serial) {
        serializeJson(jsonDoc, Serial);
        Serial.println();
    }

    // Send JSON via software serial
    serializeJson(jsonDoc, mySerial);

    // Wait for confirmation byte from the receiving Arduino (Nano RP2040)
    unsigned long startTime = millis();
    bool confirmationReceived = false;
    while (millis() - startTime < 1000) { // Wait for up to 1000 ms
        if (mySerial.available()) {
            char c = (char)mySerial.read();
            if (c == 'C') {
                confirmationReceived = true;
                break;
            }
        }
    }

    // Blink LEDs based on errors or Serial availability or confirmation from Nano
    if (!sensorData.error.isEmpty() || !Serial || !confirmationReceived) {
        digitalWrite(GREEN_LED_PIN, LOW);
        blinkLed(RED_LED_PIN, 250, 750, 3, 3);
    }

    delay(DELAY_TIME);
}



#include <ESP8266WiFi.h>
#include <ArduinoJson.h>
#include "DataContract.h"

const char* ssid = "iDizbalans-2.4";
const char* password = "master33DENIS";

WiFiServer server(80);

SensorData sensorData;

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    server.begin();
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    // Here you would read data from the sensors and fill sensorData struct
    // For example, you can use dummy data:
    sensorData.temperature_water = 23.5;
    sensorData.temperature_air = 24.7;
    sensorData.humidity = 48.9;
    sensorData.light = 350.0;
    sensorData.error = ""; // Clear previous errors

    // Check for client connections
    WiFiClient client = server.available();
    if (client) {
        String currentLine = "";
        while (client.connected()) {
            if (client.available()) {
                char c = client.read();
                if (c == '\n') {
                    // If the new line is blank, you have got the last line of the client request
                    if (currentLine.length() == 0) {
                        // Send a standard HTTP response header
                        client.println("HTTP/1.1 200 OK");
                        client.println("Content-type:application/json");
                        client.println("Connection: close");
                        client.println();

                        // Use the serializeSensorDataToJson function to create the JSON response
                        StaticJsonDocument<256> jsonDoc;
                        serializeSensorDataToJson(sensorData, jsonDoc);
                        serializeJson(jsonDoc, client);
                        client.println();
                        break;
                    }
                    else { // If you got a newline, then clear currentLine
                        currentLine = "";
                    }
                }
                else if (c != '\r') { // If you got anything else, add it to the currentLine
                    currentLine += c;
                }
            }
        }
        client.stop(); // Close the connection
    }
}
