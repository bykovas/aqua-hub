#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <PubSubClient.h>
#include <ArduinoOTA.h>

// Specify your Wi-Fi SSID and password
const char* ssid = "";
const char* password = "";

// MQTT server address
const char* mqtt_server = "192.168.1.11";

WiFiClient espClient;
PubSubClient client(espClient);

ESP8266WebServer server(80);

String serialData = "";

unsigned long lastMsgTime = 0;
const long interval = 5000;  // Message sending interval in milliseconds

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

void handleData() {
    publishMessage("/logs", "Handling data request");
    if (server.method() == HTTP_GET) {
        server.send(200, "text/plain", serialData);
        publishMessage("/logs", "GET Request processed");
    }
    else if (server.method() == HTTP_POST) {
        if (!server.hasArg("plain")) {
            server.send(200, "text/plain", "Body not received");
            publishMessage("/logs", "POST Request failed: No body received");
            return;
        }
        String message = server.arg("plain");
        publishMessage("/logs", "POST received: " + message);
        server.send(200, "application/json", "{\"result\":\"received\"}");
        publishMessage("/logs", "POST Request processed");
    }
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

void setup_ota() {
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
}

void reconnect() {
    publishMessage("/logs", "Attempting to reconnect MQTT");
    while (!client.connected()) {
        if (client.connect("ESP8266Client")) {
            publishMessage("/logs", "MQTT Reconnected");
        }
        else {
            delay(5000);
            publishMessage("/logs", "MQTT Reconnect failed, retrying...");
        }
    }
}

void setup() {
    Serial.begin(9600);
    setup_wifi();
    client.setServer(mqtt_server, 1883);
    setup_ota();
    server.on("/data", handleData);
    server.begin();
    publishMessage("/logs", "Server started");
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