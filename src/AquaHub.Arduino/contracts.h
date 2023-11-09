// DataContract.h
#ifndef DATA_CONTRACT_H
#define DATA_CONTRACT_H

#include <ArduinoJson.h>

// Definition of the data structure for sensor readings
struct SensorData {
    float temperature_water;
    float temperature_air;
    float humidity;
    float light;
    String error;
};

// Function to serialize sensor data to JSON
void serializeSensorDataToJson(const SensorData& data, JsonDocument& doc) {
    doc["temperature_water"] = data.temperature_water;
    doc["temperature_air"] = data.temperature_air;
    doc["humidity"] = data.humidity;
    doc["light"] = data.light;
    // Include the error message if it's not empty
    if (data.error != "") {
        doc["error"] = data.error;
    }
}

// Function to deserialize sensor data from JSON
void deserializeJsonToSensorData(JsonDocument& doc, SensorData& data) {
    // Use | operator to provide default values in case of missing fields
    data.temperature_water = doc["temperature_water"] | 0.0;
    data.temperature_air = doc["temperature_air"] | 0.0;
    data.humidity = doc["humidity"] | 0.0;
    data.light = doc["light"] | 0.0;
    // Check if the "error" field exists and if so, read it into the error string
    if (doc.containsKey("error")) {
        data.error = doc["error"].as<String>();
    }
}

#endif // DATA_CONTRACT_H