#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoOTA.h>

const char* ssid = "";
const char* password = "";

const char* mqtt_server = "192.168.1.11";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsgTime = 0;
const long interval = 5000;

String serialData = "";

void publishMessage(const char* topic, const String& message) {
    if (!client.connected()) {
        Serial.println("MQTT client not connected, message not sent.");
        return;
    }
    char msg[250];
    snprintf(msg, 250, "%s", message.c_str());
    client.publish(topic, msg);
    Serial.print("Published to ");
    Serial.print(topic);
    Serial.print(": ");
    Serial.println(message);
}

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    for (int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
}

void setup_wifi() {
    publishMessage("/logs", "Starting WiFi connection");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        publishMessage("/logs", "Waiting for WiFi connection...");
    }
    publishMessage("/logs", "WiFi connected, IP: " + WiFi.localIP().toString());
}

void reconnect() {
    // Loop until we're reconnected
    while (!client.connected()) {
        publishMessage("/logs", "Attempting to reconnect MQTT");
        // Attempt to connect
        if (client.connect("ESP8266Client")) {
            publishMessage("/logs", "MQTT Reconnected");
            // Subscribe to the topic
            client.subscribe("/esp8266/cmd");
        }
        else {
            // Wait 5 seconds before retrying
            delay(5000);
        }
    }
}

void setup() {
    Serial.begin(9600);
    setup_wifi();
    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);

    publishMessage("/logs", "Setting up OTA");
    ArduinoOTA.onStart([]() {
        publishMessage("/logs", "OTA Start");
        });
    ArduinoOTA.onEnd([]() {
        publishMessage("/logs", "OTA End");
        });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        publishMessage("/logs", "OTA Progress: " + String(progress / (total / 100)) + "%");
        });
    ArduinoOTA.onError([](ota_error_t error) {
        publishMessage("/logs", "OTA Error: " + String(error));
        });
    ArduinoOTA.begin();
    publishMessage("/logs", "OTA Setup complete");

    ArduinoOTA.begin();

    reconnect();
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();
    ArduinoOTA.handle();

    while (Serial.available() > 0) {
        serialData = Serial.readStringUntil('\n');
    }


    unsigned long now = millis();
    if (now - lastMsgTime > interval) {
        lastMsgTime = now;
        publishMessage("/esp8266", serialData);
        publishMessage("/logs", "Published data to /esp8266");
    }
}