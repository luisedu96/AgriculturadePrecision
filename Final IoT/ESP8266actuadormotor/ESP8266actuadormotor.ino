//Programa para ESP8266 actuador motor

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Adafruit_NeoPixel.h>

const char* ssid = "MARTINEZ_EXT";
const char* password = "71314912";
#define pinm 14 //motor
#define LED_BUILTIN 2

static String actuadores="";
//Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
void setup() {
  pinMode(LED_BUILTIN, OUTPUT); 
  Serial.begin(9600);
  pinMode(pinm, OUTPUT);
  delay(500);
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi..");
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(800); // Esperar un segundo
    // Apagar el LED
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print(".");
  }
  Serial.println("Connected to the WiFi network");
 
}
 
void loop() {
 
  if ((WiFi.status() == WL_CONNECTED)) { //Check the current connection status
 
    HTTPClient http;
 
    http.begin("http://54.91.180.147/pedir"); //Specify the URL
    int httpCode = http.GET();                                        //Make the request
 
    if (httpCode > 0) { //Check for the returning code
 
        String payload = http.getString(); //contenido de la trama enviada del servidor en respuesta a la petición
        actuadores = payload;
        Serial.println(httpCode); //confirmacion de estado del servidor
        Serial.println(payload); 
      }
 
    else {
      Serial.println("Error on HTTP request");
    }
 
    http.end(); //Free the resources
  }
  actuar();
  delay(12000);
 
}
void actuar()
{
  String motor = getValue(actuadores,';', 0); //split() devuelve el primer comando de la trama enviada del servidor
  //String luz = getValue(actuadores, ';', 1);
  //Serial.println(motor+luz);
  if(motor=="1")
  {
    Serial.println("regando");
    digitalWrite(pinm, HIGH);
    delay(5500);
    digitalWrite(pinm, LOW);
  }
  else if(motor=="0")
  {
    digitalWrite(pinm, LOW);
  }
}

String getValue(String data, char separator, int index) //Split
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}
