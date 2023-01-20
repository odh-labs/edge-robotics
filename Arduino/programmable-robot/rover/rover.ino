#include <WiFi.h>
#include <aREST.h>

#include "RoverC.h"
#include "RoverCommands.h"

// ******************************************************************************************
// #define one or the other and not both: _LEADER or _FOLLOWER.  
// LEADER sends movement commands to a MQTT topic and never receives from the MQTT topic
// FOLLOWER receives from a MQTT topic and never sends movement commands to the MQTT topic
// ******************************************************************************************
#define _MQTT
#define _LEADER
//#define _FOLLOWER
// ******************************************************************************************

#ifdef _MQTT
#include <PubSubClient.h>
#include <ArduinoJson.h>
#endif

#define MAX_MSG_LENGTH 100

// Create aREST instance
aREST rest = aREST();

// WiFi parameters
const char* ssid = "Kardinia701";
const char* password = "myPassword";



// Create an instance of the server
WiFiServer server(80);

char ip[16], cmd[16], message[MAX_MSG_LENGTH + 1];

RoverCommands rc = RoverCommands();

#ifdef _MQTT

// MQTT parameters
const char* mqttServer = "broker.hivemq.com";
const int mqttPort = 1883;
const char* mqttUser = "rhtest";
const char* mqttPassword = "rhtest";

const char* mqttTopic = "movement";
// ******************************************************************************************
#ifdef _LEADER
const char* restId = "1";
const char* restName = "LEAD";
const char* mqttClientName = "LEAD";
#endif
// ******************************************************************************************
#ifdef _FOLLOWER
const char* restId = "2";
const char* restName = "FOLLOW";
const char* mqttClientName = "FOLLOW";

DynamicJsonDocument doc(100);
char jsonMsg[100];
// create the clients
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// this callback function is called when a MQTT message is received
// The payload is in json. Here is a sample:
// { "id" : "andy", "cmd" : "forward", "time" : "1090278" }
void processMqttMsg(char* topic, byte* payload, unsigned int length) {
  // clear scheduled event, if any (there can be only one event outstanding)
  clearScheduledEvents();

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i=0;i<length;i++) {
    Serial.print((char)payload[i]);
    jsonMsg[i] = char(payload[i]);
  }
  jsonMsg[length] = 0;
  Serial.println();
  deserializeJson(doc, jsonMsg);
  JsonObject object = doc.as<JsonObject>();
  const char* command = object["cmd"];
  Serial.println(command);
  execCommand(command);
}
#endif
// ******************************************************************************************

// Send MQTT message to a specific topic
int publishMqttMsg(char *cmd) {
  snprintf(message, MAX_MSG_LENGTH, "{ \"id\" : \"%s\", \"cmd\" : \"%s\", \"time\" : \"%ld\" }", rc.getName(),  cmd, millis());
  Serial.println(message);
  return mqttClient.publish(mqttTopic, message);
}
#else
const char* restId = "3";
const char* restName = "WIFI_ROBOT";
#endif

// the setup routine runs once when M5StickC starts up
void setup(){ 

  // Start Serial
  Serial.begin(115200);
  Serial.println("Initializing...");
  
  // Function to be exposed
  rest.function("exec",execCommand);

  // Give name & ID to the device (ID should be 6 characters long)
  rest.set_id(restId);
  rest.set_name(restName);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Initialize the M5StickC object
  M5.begin();

  // display IP address on LCD
  M5.Lcd.setRotation(3);
  M5.Lcd.setTextColor(BLUE);
  M5.Lcd.setCursor(0, 5, 2);
  WiFi.localIP().toString().toCharArray(ip, 16);
  M5.Lcd.printf(ip);

  Serial.println(WiFi.localIP());
  
  // Start the server
  server.begin();
  Serial.println("Server started");

#ifdef _MQTT
  // connect to MQTT server
  mqttClient.setServer(mqttServer, mqttPort);
  while (!mqttClient.connected()) {
      Serial.println("Connecting to MQTT...");
   
      if (mqttClient.connect(mqttClientName, mqttUser, mqttPassword )) {
   
        Serial.println("connected");
        lcdMessage("MQTT Connected.");

// ******************************************************************************************
#ifdef _FOLLOWER
        mqttClient.setCallback(processMqttMsg);
        mqttClient.subscribe(mqttTopic);
#endif
// ******************************************************************************************

      } else {
   
        Serial.print("failed with state ");
        Serial.print(mqttClient.state());
        delay(2000);
   
      }
  }
#endif

  RoverC_Init();
  lcdMessage("Rover Ready.");
}

// the loop routine runs over and over again forever
void loop() {
  //snprintf(message, MAX_MSG_LENGTH, "Speed: %d", rc.getSpeed());
  //lcdMessage(message);

  // Handle REST calls
  WiFiClient client = server.available();
  if (client > 0) {
    // clear scheduled event, if any (there can be only one event outstanding)
    clearScheduledEvents();
    rest.handle(client);
  } else {
    // check if scheduled event is due for execution
    if (! SchedulerQueue::getInstance()->getEventQueue()->isEmpty()) {
      Event event = SchedulerQueue::getInstance()->getEventQueue()->getHead();
      snprintf(message, MAX_MSG_LENGTH, "Process: QueueLength=%d, event.time=%ld, event.action=%d, time: %ld", 
        SchedulerQueue::getInstance()->getEventQueue()->itemCount(), event.time, event.action, millis());
      Serial.println(message);
      if (millis() >= event.time) {
        if (event.action == COMPLETE) {
          rc.completeExecute();
        }
        else if (event.action == CONTINUE) {
          rc.continueExecute();
        }
        event = SchedulerQueue::getInstance()->getEventQueue()->dequeue();
      }
    }
  }

#ifdef _MQTT
  // poll for MQTT message and maintain connection
  mqttClient.loop();
#endif
}


// display a line of text on LCD
void lcdMessage(char *msg) {
  M5.Lcd.fillRect(0, 20, 160, 20, TFT_BLACK);
  M5.Lcd.setCursor(0, 20, 2);
  M5.Lcd.setTextColor(TFT_RED,TFT_RED);
  M5.Lcd.drawCentreString(msg, 10, 20, 2);
}

// Function to be executed when REST service is invoked
// The REST service is invoked using: http://hostOrIP/exec?param=remoteCmds
int execCommand(String command) {
  Serial.print("Cmd: ");
  Serial.println(command);

  command.toCharArray(cmd, 16);
  lcdMessage(cmd);

#ifdef _MQTT
// ******************************************************************************************
#ifdef _LEADER
  // publish the movement command to MQTT topic
  if (!publishMqttMsg(cmd)) {
    Serial.print("MQTT failed: ");
    Serial.println(mqttClient.state());
    lcdMessage("MQTT failed");
  }
#endif
// ******************************************************************************************
#endif

  return rc.execCommand(cmd);

}

void clearScheduledEvents() {
    // clear scheduled event, if any (there can be only one event outstanding)
    if (! SchedulerQueue::getInstance()->getEventQueue()->isEmpty()) {
      for (int i = 0; i < SchedulerQueue::getInstance()->getEventQueue()->itemCount(); i++) {
        Event event = SchedulerQueue::getInstance()->getEventQueue()->dequeue();
        snprintf(message, MAX_MSG_LENGTH, "Clear: QueueLength=%d, event.time=%ld, event.action=%d, time: %ld", 
          SchedulerQueue::getInstance()->getEventQueue()->itemCount(), event.time, event.action, millis());
        Serial.println(message);
      }
      rc.completeExecute();
    }
}
