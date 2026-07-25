/*
 * ESP32 Smart Grid AC Telemetry Node Firmware
 * Target Microcontroller: ESP32 DevKit v1
 * Sensors: PZEM-004T v3.0 / INA219 AC Current & Voltage Transducer
 * Protocols: WiFi, MQTT (PubSubClient), ArduinoJson
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// --- WiFi Credentials ---
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";

// --- MQTT Broker Configuration ---
const char* MQTT_BROKER = "broker.hivemq.com";
const int   MQTT_PORT   = 1883;
const char* MQTT_TOPIC  = "esp32/smartgrid/telemetry";

WiFiClient espClient;
PubSubClient client(espClient);

// --- Pin Definitions & Dummy Sensor Variables ---
const char* NODE_ID = "ESP32_SUBSTATION_01";
unsigned long lastSendTime = 0;
const int sendIntervalMs = 3000; // Send telemetry every 3 seconds

void setupWiFi() {
  delay(10);
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected! IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32GridNode-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected to Broker!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setupWiFi();
  client.setServer(MQTT_BROKER, MQTT_PORT);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastSendTime > sendIntervalMs) {
    lastSendTime = now;

    // Simulated 3-Phase AC Telemetry Readings (Replace with actual PZEM-004T Hardware calls)
    float v_a = 230.0 + random(-30, 30) / 10.0;
    float v_b = 229.5 + random(-30, 30) / 10.0;
    float v_c = 230.8 + random(-30, 30) / 10.0;

    float i_a = 15.2 + random(-10, 10) / 10.0;
    float i_b = 14.8 + random(-10, 10) / 10.0;
    float i_c = 15.0 + random(-10, 10) / 10.0;

    float pf = 0.95;
    float p_kw = (v_a * i_a + v_b * i_b + v_c * i_c) * pf / 1000.0;
    float q_kvar = p_kw * 0.32;
    float freq = 50.0;

    // Construct JSON Payload
    StaticJsonDocument<300> doc;
    doc["node_id"] = NODE_ID;
    doc["voltage_a"] = v_a;
    doc["voltage_b"] = v_b;
    doc["voltage_c"] = v_c;
    doc["current_a"] = i_a;
    doc["current_b"] = i_b;
    doc["current_c"] = i_c;
    doc["active_power"] = p_kw;
    doc["reactive_power"] = q_kvar;
    doc["power_factor"] = pf;
    doc["frequency"] = freq;
    doc["status"] = "NORMAL";

    char jsonBuffer[512];
    serializeJson(doc, jsonBuffer);

    Serial.print("Publishing MQTT Payload: ");
    Serial.println(jsonBuffer);

    client.publish(MQTT_TOPIC, jsonBuffer);
  }
}
