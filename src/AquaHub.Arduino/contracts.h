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
    float air_fan;
    String error;
};

// Function to serialize sensor data to JSON
void serializeSensorDataToJson(const SensorData& data, JsonDocument& doc) {
    JsonArray sensors = doc.createNestedArray("sensors");

    JsonObject sensorTempWater = sensors.createNestedObject();
    sensorTempWater["name"] = "water_temp";
    sensorTempWater["value"] = data.temperature_water;

    JsonObject sensorTempAir = sensors.createNestedObject();
    sensorTempAir["name"] = "air_temp";
    sensorTempAir["value"] = data.temperature_air;

    JsonObject sensorHumidity = sensors.createNestedObject();
    sensorHumidity["name"] = "humidity";
    sensorHumidity["value"] = data.humidity;

    JsonObject sensorLight = sensors.createNestedObject();
    sensorLight["name"] = "lux";
    sensorLight["value"] = data.light;

    JsonObject sensorAirFan = sensors.createNestedObject();
    sensorAirFan["name"] = "air_fan";
    sensorAirFan["value"] = data.air_fan;

    if (data.error.length() > 0) {
        doc["errors"] = data.error;
    }
    else {
        doc["errors"] = "";
    }
}

#endif  // DATA_CONTRACT_H