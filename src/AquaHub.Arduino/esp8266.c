#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "";
const char* password = "";

ESP8266WebServer server(80);
String serialData = "";

void handleData() {
    if (server.method() == HTTP_GET) {
        server.send(200, "text/plain", serialData);
    }
    else if (server.method() == HTTP_POST) {
        if (server.hasArg("plain") == false) {
            server.send(200, "text/plain", "Body not received");
            return;
        }
        String message = server.arg("plain");
        Serial.println(message);
        server.send(200, "application/json", "{\"result\":\"received\"}");
    }
}

void setup() {
    Serial.begin(9600);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }

    //Serial.println("");
    //Serial.println("WiFi connected");
    //Serial.println("IP address: ");
    //Serial.println(WiFi.localIP());

    server.on("/data", handleData);

    server.begin();
}

void loop() {
    server.handleClient();

    while (Serial.available() > 0) {
        serialData = Serial.readStringUntil('\n');
    }
}