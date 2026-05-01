#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal_I2C.h>
#include "time.h"

// --- CONFIGURATION PINS ---
#define SS_PIN 5
#define RST_PIN 4
#define BTN_IN 13    // Bouton Vert
#define BTN_OUT 14   // Bouton Bleu
#define LED_GREEN 25
#define LED_RED 26
#define BUZZER 27

// --- OBJETS ---
MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);
WiFiClientSecure espClient;
PubSubClient client(espClient);

// --- IDENTIFIANTS RÉSEAU & MQTT ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "c69c5ab4c09848f88fe18d9374121871.s1.eu.hivemq.cloud";
const char* mqtt_user = "davincii5";
const char* mqtt_pass = "Davincii123456";

// --- SERVEUR TEMPS (NTP) ---
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600; // GMT+1 (Maroc)
const int   daylightOffset_sec = 0;

void setup() {
  Serial.begin(115200);

  pinMode(BTN_IN, INPUT_PULLUP);
  pinMode(BTN_OUT, INPUT_PULLUP);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("SIRH Smart Ent.");
  lcd.setCursor(0, 1);
  lcd.print("Connexion...");

  SPI.begin();
  rfid.PCD_Init();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  // Synchronisation de l'heure réelle
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  // Configuration SSL pour HiveMQ Cloud
  espClient.setInsecure(); 
  client.setServer(mqtt_server, 8883);

  lcd.clear();
  lcd.print("Pret a pointer!");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connexion HiveMQ...");
    if (client.connect("ESP32_Terminal", mqtt_user, mqtt_pass)) {
      Serial.println("Connecte !");
    } else {
      Serial.print("Echec, code: ");
      Serial.print(client.state());
      delay(3000);
    }
  }
}

void feedbackVisuel(bool success) {
  if (success) {
    digitalWrite(LED_GREEN, HIGH);
    tone(BUZZER, 1000, 200);
    delay(200);
    digitalWrite(LED_GREEN, LOW);
  } else {
    digitalWrite(LED_RED, HIGH);
    tone(BUZZER, 500, 500);
    delay(500);
    digitalWrite(LED_RED, LOW);
  }
}

void sendPointage(String matricule, String typeMouvement) {
  if (!client.connected()) reconnect();

  struct tm timeinfo;
  char timeString[50];
  if(!getLocalTime(&timeinfo)){
    strcpy(timeString, "2026-04-29T12:00:00Z"); // Fallback
  } else {
    strftime(timeString, sizeof(timeString), "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  }

  // Préparation du JSON pour Django
  StaticJsonDocument<256> doc;
  doc["matricule"] = matricule;
  doc["id_capteur"] = "ESP32_WOKWI_01";
  doc["timestamp"] = timeString;
  doc["est_justifie"] = false;
  doc["type_pointage"] = typeMouvement;

  char buffer[256];
  serializeJson(doc, buffer);

  if (client.publish("sirh/attendance", buffer)) {
    Serial.println("Pointage envoye : " + String(buffer));
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(matricule + " OK");
    lcd.setCursor(0, 1);
    lcd.print(typeMouvement);
    
    feedbackVisuel(true);
    
    delay(2000);
    lcd.clear();
    lcd.print("Pret a pointer!");
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // Détection Bouton Entrée (Vert)
  if (digitalRead(BTN_IN) == LOW) {
    sendPointage("EMP-001", "ENTREE");
    delay(1000); 
  }
  
  // Détection Bouton Sortie (Bleu)
  if (digitalRead(BTN_OUT) == LOW) {
    sendPointage("EMP-001", "SORTIE");
    delay(1000); 
  }

  // Détection RFID
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    // On simule un deuxième employé pour le badge RFID
    sendPointage("EMP-002", "ENTREE");
    rfid.PICC_HaltA();
    delay(1000);
  }
}