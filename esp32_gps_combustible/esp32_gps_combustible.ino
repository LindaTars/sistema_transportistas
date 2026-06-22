#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// ── WiFi ────────────────────────────────────────────────────
const char* ssid     = "vivo Y53s";
const char* password = "1234567897";
const char* serverURL = "http://172.17.0.1:8000/rutas/ping-gps";

// ── GPS ─────────────────────────────────────────────────────
HardwareSerial gpsSerial(2);
TinyGPSPlus gps;

// ── Ultrasónico HC-SR04 ──────────────────────────────────────
#define PIN_TRIG  13
#define PIN_ECHO  12

// ── Configuración del tanque ─────────────────────────────────
#define ALTURA_TANQUE_CM  30.0   
#define OFFSET_SENSOR_CM   2.0   

unsigned long ultimoEnvio = 0;
const unsigned long INTERVALO_ENVIO = 5000;

void setup() {
    Serial.begin(115200);
    delay(1000);

    // GPS
    gpsSerial.begin(9600, SERIAL_8N1, 25, 26);

  // Ultrasónico
    pinMode(PIN_TRIG, OUTPUT);
    pinMode(PIN_ECHO, INPUT);

  // WiFi
    Serial.println("Conectando a WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    }
    Serial.println("\n✅ WiFi conectado");
    Serial.print("IP del ESP32: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    // Leer GPS continuamente
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }

    if (millis() - ultimoEnvio >= INTERVALO_ENVIO) {
    ultimoEnvio = millis();

    // Medir nivel de gasolina
    float nivelPorcentaje = medirNivelGasolina();

    if (gps.location.isValid()) {
        enviarDatos(gps.location.lat(), gps.location.lng(), nivelPorcentaje);
        } else {
        Serial.printf("⌛ GPS: Satélites %d | Gasolina: %.1f%%\n",
                        gps.satellites.value(), nivelPorcentaje);
        }
    }
}

// ── Medir distancia con HC-SR04 ──────────────────────────────
float medirDistanciaCM() {
    // Enviar pulso de 10 microsegundos
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);

    // Medir tiempo de respuesta (timeout 30ms = ~5 metros máximo)
    long duracion = pulseIn(PIN_ECHO, HIGH, 30000);

  if (duracion == 0) return -1;  // sin respuesta = error

  // Distancia en cm: (velocidad sonido 343 m/s) / 2 (ida y vuelta)
  return (duracion * 0.0343) / 2.0;
}

// ── Calcular nivel de gasolina en porcentaje ─────────────────
float medirNivelGasolina() {
  // Promedio de 5 lecturas para estabilizar
    float suma = 0;
    int lecturas_validas = 0;

    for (int i = 0; i < 5; i++) {
        float d = medirDistanciaCM();
        if (d > 0) {
        suma += d;
        lecturas_validas++;
    }
    delay(60);
}

    if (lecturas_validas == 0) {
        Serial.println("Error en sensor ultrasónico");
        return -1;
    }

    float distancia_promedio = suma / lecturas_validas;

  // El sensor está arriba del tanque, mide la distancia hasta el líquido
  // Nivel = altura total - distancia medida - offset del sensor
    float nivel_cm = ALTURA_TANQUE_CM - distancia_promedio - OFFSET_SENSOR_CM;

  // Convertir a porcentaje
  float porcentaje = (nivel_cm / ALTURA_TANQUE_CM) * 100.0;

  // Limitar entre 0% y 100%
    porcentaje = constrain(porcentaje, 0.0, 100.0);

    Serial.printf("Distancia: %.1f cm | Nivel: %.1f cm | Gasolina: %.1f%%\n",
                    distancia_promedio, nivel_cm, porcentaje);

    return porcentaje;
}

// ── Enviar GPS + nivel de gasolina a Django ──────────────────
void enviarDatos(double lat, double lng, float gasolina) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi desconectado");
        return;
    }

    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"latitud\":" + String(lat, 6) +
                ",\"longitud\":" + String(lng, 6) +
                ",\"nivel_combustible\":" + String(gasolina, 1) +
                ",\"velocidad\":0}";

    int httpCode = http.POST(payload);

    if (httpCode > 0) {
        Serial.printf("Enviado [%d]: %s\n", httpCode, payload.c_str());
    } else {
        Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
    }
#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// ── WiFi ────────────────────────────────────────────────────
const char* ssid     = "vivo Y53s";
const char* password = "1234567897";
const char* serverURL = "http://10.162.152.78:8000/api/gps/";

// ── GPS ─────────────────────────────────────────────────────
HardwareSerial gpsSerial(2);
TinyGPSPlus gps;

// ── Ultrasónico HC-SR04 ──────────────────────────────────────
#define PIN_TRIG  13
#define PIN_ECHO  12

// ── Configuración del tanque ─────────────────────────────────
#define ALTURA_TANQUE_CM  30.0   // ← cambia esto por la altura real de tu tanque en cm
#define OFFSET_SENSOR_CM   2.0   // distancia mínima que el sensor necesita (punto muerto)

unsigned long ultimoEnvio = 0;
const unsigned long INTERVALO_ENVIO = 5000;

void setup() {
    Serial.begin(115200);
    delay(1000);

    // GPS
    gpsSerial.begin(9600, SERIAL_8N1, 25, 26);

    // Ultrasónico
    pinMode(PIN_TRIG, OUTPUT);
    pinMode(PIN_ECHO, INPUT);

    // WiFi
    Serial.println("Conectando a WiFi...");
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✅ WiFi conectado");
    Serial.print("IP del ESP32: ");
    Serial.println(WiFi.localIP());
}

void loop() {
    // Leer GPS continuamente
    while (gpsSerial.available() > 0) {
        gps.encode(gpsSerial.read());
    }

    if (millis() - ultimoEnvio >= INTERVALO_ENVIO) {
        ultimoEnvio = millis();

        // Medir nivel de gasolina
        float nivelPorcentaje = medirNivelGasolina();

        if (gps.location.isValid()) {
        enviarDatos(gps.location.lat(), gps.location.lng(), nivelPorcentaje);
        } else {
        Serial.printf("GPS: Satélites %d | Gasolina: %.1f%%\n",
                        gps.satellites.value(), nivelPorcentaje);
        }
    }
}

// ── Medir distancia con HC-SR04 ──────────────────────────────
float medirDistanciaCM() {
    // Enviar pulso de 10 microsegundos
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);

  // Medir tiempo de respuesta (timeout 30ms = ~5 metros máximo)
    long duracion = pulseIn(PIN_ECHO, HIGH, 30000);

    if (duracion == 0) return -1;  // sin respuesta = error

    // Distancia en cm: (velocidad sonido 343 m/s) / 2 (ida y vuelta)
    return (duracion * 0.0343) / 2.0;
}

// ── Calcular nivel de gasolina en porcentaje ─────────────────
float medirNivelGasolina() {
    // Promedio de 5 lecturas para estabilizar
    float suma = 0;
    int lecturas_validas = 0;

    for (int i = 0; i < 5; i++) {
        float d = medirDistanciaCM();
        if (d > 0) {
        suma += d;
        lecturas_validas++;
        }
        delay(60);
    }

    if (lecturas_validas == 0) {
        Serial.println("Error en sensor ultrasónico");
        return -1;
    }

    float distancia_promedio = suma / lecturas_validas;

    // El sensor está arriba del tanque, mide la distancia hasta el líquido
    // Nivel = altura total - distancia medida - offset del sensor
    float nivel_cm = ALTURA_TANQUE_CM - distancia_promedio - OFFSET_SENSOR_CM;

    // Convertir a porcentaje
    float porcentaje = (nivel_cm / ALTURA_TANQUE_CM) * 100.0;

    // Limitar entre 0% y 100%
    porcentaje = constrain(porcentaje, 0.0, 100.0);

    Serial.printf("Distancia: %.1f cm | Nivel: %.1f cm | Gasolina: %.1f%%\n",
                    distancia_promedio, nivel_cm, porcentaje);

    return porcentaje;
}

// ── Enviar GPS + nivel de gasolina a Django ──────────────────
void enviarDatos(double lat, double lng, float gasolina) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi desconectado");
        return;
    }

    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");

    String payload = "{\"lat\":" + String(lat, 6) +
                    ",\"lng\":" + String(lng, 6) +
                    ",\"gasolina\":" + String(gasolina, 1) + "}";

    int httpCode = http.POST(payload);

    if (httpCode > 0) {
        Serial.printf("Enviado [%d]: %s\n", httpCode, payload.c_str());
    } else {
        Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
    }
    http.end();
}