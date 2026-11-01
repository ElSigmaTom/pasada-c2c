/* PASADA ESP32-C3 serial-only scaffold. No GPIO signal output or radio is enabled.
 * Requires Arduino-ESP32 and ArduinoJson 7. See docs/IMPLEMENTATION_GUIDE.md.
 * Hardware build and bench verification have not been performed in this draft.
 */
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Preferences.h>

Preferences storage;
JsonDocument deviceConfig;
String line;
unsigned long lastHeartbeat = 0;
unsigned long sequence = 0;

void emit(JsonDocument &d) { serializeJson(d, Serial); Serial.println(); }

void handleCommand(const String &raw) {
  JsonDocument request, response;
  if (deserializeJson(request, raw)) return;
  response["request_id"] = request["request_id"].as<String>();
  response["ok"] = true;
  String command = request["command"].as<String>();
  if (command == "get_info") {
    response["protocol"] = "pasada.serial/0.1.0";
    response["firmware_version"] = "0.1.0";
    response["output_mode"] = "serial-only";
    response["radio_ready"] = false;
    response["sensor_ready"] = false;
    response["chip_id"] = String((uint32_t)(ESP.getEfuseMac() & 0xffffffff), HEX);
  } else if (command == "get_config") {
    response["config"].set(deviceConfig.as<JsonObject>());
  } else if (command == "set_config") {
    JsonObject c = request["config"].as<JsonObject>();
    String role = c["role"].as<String>();
    bool valid = c["schema"] == "pasada.device/0.1.0" &&
      c["output_mode"] == "serial-only" && c["security_mode"] == "simulation" &&
      c["device_id"].is<const char*>() &&
      (role == "sensor" || role == "controller" || role == "beacon") &&
      !(c["installation_ready"].is<bool>() && c["installation_ready"].as<bool>() == false);
    int channel = c["esp_now_channel"] | 0;
    if (!valid || channel < 1 || channel > 11) {
      response["ok"] = false; response["error"] = "Unsupported or incomplete serial-only configuration";
    } else {
      String encoded; serializeJson(c, encoded);
      if (encoded.length() > 16384 || storage.putString("config", encoded) == 0) {
        response["ok"] = false; response["error"] = "Configuration persistence failed";
      } else {
        deviceConfig.clear(); deserializeJson(deviceConfig, storage.getString("config", "{}"));
        response["persisted"] = true;
      }
    }
  } else {
    response["ok"] = false; response["error"] = "Unknown command";
  }
  emit(response);
}

void setup() {
  Serial.begin(115200);
  storage.begin("pasada-draft", false);
  deserializeJson(deviceConfig, storage.getString("config", "{}"));
  line.reserve(17000);
}

void loop() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == '\n') { handleCommand(line); line = ""; }
    else if (ch != '\r') {
      if (line.length() < 17000) line += ch;
      else line = "";
    }
  }
  if (millis() - lastHeartbeat >= 1000) {
    lastHeartbeat = millis();
    JsonDocument heartbeat;
    heartbeat["schema"] = "pasada.serial-heartbeat/0.1.0";
    heartbeat["device_id"] = deviceConfig["device_id"] | "UNCONFIGURED";
    heartbeat["sequence"] = ++sequence;
    heartbeat["uptime_ms"] = millis();
    heartbeat["clock_synchronized"] = false;
    heartbeat["sensor_ready"] = false;
    heartbeat["radio_ready"] = false;
    heartbeat["physical_outputs_enabled"] = false;
    emit(heartbeat);
  }
}
