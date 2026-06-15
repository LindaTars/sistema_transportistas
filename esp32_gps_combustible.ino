/* ============================================================
   ESP32 + GPS (NEO-6M/NEO-8M) + HC-SR04 (nivel de combustible)
   Envía ping periódico al backend: POST /rutas/ping-gps
   ============================================================

   Conexiones:
   -----------
   GPS NEO-6M/NEO-8M (UART):
     GPS TX  -> ESP32 GPIO16 (RX2)
     GPS RX  -> ESP32 GPIO17 (TX2)
     GPS VCC -> 3.3V o 5V (según módulo)
     GPS GND -> GND

   HC-SR04 (sensor ultrasónico en el tanque):
     TRIG -> ESP32 GPIO5
     ECHO -> ESP32 GPIO18  (usar divisor de voltaje 5V->3.3V en ECHO)
     VCC  -> 5V
     GND  -> GND

   Librerías necesarias (Arduino IDE > Library Manager):
     - TinyGPSPlus  (by Mikal Hart)
     - ArduinoJson  (by Benoit Blanchon)
     (WiFi.h y HTTPClient.h ya vienen incluidas con el core de ESP32)
   ============================================================ */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// ───────────────────────── CONFIGURACIÓN ─────────────────────────

// Wi-Fi
const char* WIFI_SSID     = "TU_RED_WIFI";
const char* WIFI_PASSWORD = "TU_PASSWORD";

// Backend (usa la IP de la máquina donde corre el API, NO 127.0.0.1,
// porque el ESP32 es otro dispositivo en la red)
const char* API_URL = "http://192.168.1.100:8000/rutas/ping-gps";

// Intervalo de envío del ping (ms) -> 30 segundos
const unsigned long INTERVALO_PING = 30000;

// ───────────────────────── PINES ─────────────────────────

// GPS por Serial2 (UART hardware del ESP32)
#define GPS_RX_PIN 16   // ESP32 RX2 <- GPS TX
#define GPS_TX_PIN 17   // ESP32 TX2 -> GPS RX
#define GPS_BAUD   9600

// HC-SR04
#define TRIG_PIN 5
#define ECHO_PIN 18

// Altura total del tanque en cm (para referencia / depuración)
// El backend recibe el valor crudo en cm que mide el sensor
// (distancia entre el sensor y el nivel del combustible).
#define ALTURA_TANQUE_CM 30.0

// ───────────────────────── OBJETOS GLOBALES ─────────────────────────

TinyGPSPlus gps;
HardwareSerial gpsSerial(2);   // UART2 del ESP32

unsigned long ultimoEnvio = 0;

// ============================================================
//                        SETUP
// ============================================================
void setup() {
    Serial.begin(115200);
    delay(500);

    // Pines del HC-SR04
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    digitalWrite(TRIG_PIN, LOW);

    // GPS
    gpsSerial.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

    conectarWiFi();

    Serial.println("✅ Listo. Esperando señal GPS...");
}

// ============================================================
//                        LOOP
// ============================================================
void loop() {
    // Alimentar al parser del GPS con todo lo que llega por UART2
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }

    // Reconectar Wi-Fi si se cae
    if (WiFi.status() != WL_CONNECTED) {
        conectarWiFi();
    }

    // Enviar ping cada INTERVALO_PING ms
    unsigned long ahora = millis();
    if (ahora - ultimoEnvio >= INTERVALO_PING) {
        ultimoEnvio = ahora;
        enviarPing();
    }
}

// ============================================================
//                  CONECTAR WIFI
// ============================================================
void conectarWiFi() {
    if (WiFi.status() == WL_CONNECTED) return;

    Serial.print("Conectando a WiFi");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    unsigned long inicio = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - inicio < 15000) {
        delay(300);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi conectado. IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("\n⚠️ No se pudo conectar a WiFi, se reintentará...");
    }
}

// ============================================================
//          LEER NIVEL DE COMBUSTIBLE (HC-SR04 -> cm)
// ============================================================
float leerNivelCombustibleCM() {
    // Pulso de disparo
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Duración del eco (timeout 30ms ~ 5m de distancia máx.)
    long duracion = pulseIn(ECHO_PIN, HIGH, 30000);

    if (duracion == 0) {
        // Sin lectura válida -> reportar distancia máxima como "tanque vacío"
        return ALTURA_TANQUE_CM;
    }

    // distancia (cm) = duración(us) * velocidad_sonido(cm/us) / 2
    float distanciaCM = duracion * 0.0343 / 2.0;

    // Limitar a rango razonable [0, ALTURA_TANQUE_CM]
    if (distanciaCM < 0) distanciaCM = 0;
    if (distanciaCM > ALTURA_TANQUE_CM) distanciaCM = ALTURA_TANQUE_CM;

    return distanciaCM;
}

// ============================================================
//          ENVIAR PING GPS + COMBUSTIBLE AL BACKEND
// ============================================================
void enviarPing() {
    // Necesitamos al menos una posición válida del GPS
    if (!gps.location.isValid()) {
        Serial.println("⏳ Esperando fix de GPS...");
        return;
    }

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("⚠️ Sin WiFi, no se puede enviar el ping.");
        return;
    }

    double  latitud      = gps.location.lat();
    double  longitud     = gps.location.lng();
    double  velocidadKmh = gps.speed.isValid() ? gps.speed.kmph() : 0.0;
    float   nivelCombCM  = leerNivelCombustibleCM();

    // Construir JSON
    StaticJsonDocument<200> doc;
    doc["latitud"]           = latitud;
    doc["longitud"]          = longitud;
    doc["nivel_combustible"] = nivelCombCM;
    doc["velocidad"]         = velocidadKmh;

    String payload;
    serializeJson(doc, payload);

    Serial.println("📡 Enviando ping: " + payload);

    HTTPClient http;
    http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");

    int codigoRespuesta = http.POST(payload);

    if (codigoRespuesta > 0) {
        String respuesta = http.getString();
        Serial.println("✅ Respuesta (" + String(codigoRespuesta) + "): " + respuesta);
    } else {
        Serial.println("❌ Error al enviar ping: " + http.errorToString(codigoRespuesta));
    }

    http.end();
}
