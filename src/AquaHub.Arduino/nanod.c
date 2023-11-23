#include <DHT.h>
#include <SPI.h>
#include <WiFiNINA.h>
#include <Wire.h>
#include <BH1750.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// WiFi credentials placeholders
const char ssid[] = "YOUR_SSID";
const char pass[] = "YOUR_PASSWORD";

unsigned long previousMillis = 0;  // Stores last time temperature was published
const long interval = 2000;        // Interval at which to read the sensors (milliseconds)
float temperatureAir, humidity, lightLevel, temperatureWater;

int status = WL_IDLE_STATUS;
WiFiServer server(80);
BH1750 lightMeter;
DHT dht(2, DHT22);
OneWire oneWire(3);
DallasTemperature sensors(&oneWire);

void setup() {
    if (Serial) {
        Serial.begin(9600);
        // Only print to serial if the serial interface is available
        Serial.println("Serial is available.");
    }

    while (status != WL_CONNECTED) {
        // Attempt to connect to WiFi network
        status = WiFi.begin(ssid, pass);
        delay(10000);
        if (Serial) {
            Serial.print("Attempting to connect to Network named: ");
            Serial.println(ssid);
            if (status == WL_CONNECTED && Serial) {
                Serial.println("Connected to wifi");
            }
        }
    }

    // Sensor initialization
    Wire.begin();
    lightMeter.begin();
    dht.begin();
    sensors.begin();

    // Start the server
    server.begin();
}

void loop() {
    // Ensure WiFi is connected
    reconnectWiFi();

    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        readSensors();
    }

    WiFiClient client = server.available();
    if (client) {
        serveClient(client);
    }
}

void readSensors() {
    temperatureAir = dht.readTemperature();
    humidity = dht.readHumidity();
    lightLevel = lightMeter.readLightLevel();
    sensors.requestTemperatures();
    temperatureWater = sensors.getTempCByIndex(0);

    if (isnan(temperatureAir) || isnan(humidity) || temperatureWater == DEVICE_DISCONNECTED_C) {
        if (Serial) {
            Serial.println("Failed to read from sensors!");
        }
        temperatureAir = humidity = temperatureWater = 0.0; // Assign default values
    }
}

void serveClient(WiFiClient& client) {
    boolean currentLineIsBlank = true;
    while (client.connected()) {
        if (client.available()) {
            char c = client.read();
            if (c == '\n' && currentLineIsBlank) {
                sendHttpResponse(client);
                break;
            }
            if (c == '\n') {
                currentLineIsBlank = true;
            }
            else if (c != '\r') {
                currentLineIsBlank = false;
            }
        }
    }
    client.stop();
}

void sendHttpResponse(WiFiClient& client) {
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: application/json");
    client.println("Connection: close");
    client.println();
    client.print("{\"lux\":");
    client.print(lightLevel);
    client.print(",\"temperature_air\":");
    client.print(temperatureAir);
    client.print(",\"humidity\":");
    client.print(humidity);
    client.print(",\"temperature_water\":");
    client.print(temperatureWater);
    client.println("}");
}

void reconnectWiFi() {
    if (WiFi.status() != WL_CONNECTED) {
        if (Serial) {
            Serial.println("WiFi connection lost. Trying to reconnect...");
        }
        while (WiFi.status() != WL_CONNECTED) {
            status = WiFi.begin(ssid, pass);
            delay(5000);
        }
        if (Serial) {
            Serial.println("Reconnected to WiFi.");
        }
    }
}