#include <Wire.h>
#include <ClosedCube_HDC1080.h>
#include <BH1750FVI.h>
#include <Adafruit_NeoPixel.h>
//#include <SoftwareSerial.h>

const int sensorPin = A0; //sensor humedad suelo
//const int motorPin = 5;
#define D0 23 //motor
#define PIN 16 //leds
#define NUMPIXELS 12 //numero leds

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800); 

ClosedCube_HDC1080 sensorT;
BH1750FVI Luxometro(BH1750FVI::k_DevModeContLowRes);
void setup() {
   pixels.begin();
   pinMode(D0, OUTPUT);
   pinMode(5, OUTPUT);
   //pinMode(2, OUTPUT);
   //pinMode(LED_BUILTIN, OUTPUT);
   digitalWrite(D0, LOW);
   digitalWrite(5, HIGH);
   Serial.begin(115200);
   sensorT.begin(0x40);
   Luxometro.begin();
}

void loop() 
{ 
   pixels.clear();
   float humedad = 0;
   int num=20;
   while(num!=0)
   {
    float suma = analogRead(sensorPin);
    humedad = humedad+suma;
    num=num-1;
   }
   humedad=humedad/20;
   
   float lecturaporcentaje = map(humedad, 4095, 2430, 0, 100);
   Serial.println(humedad);
   //Serial.println(lecturaporcentaje);
  
   if(lecturaporcentaje<10)
   {
    Serial.println("El sensor está desconectado o fuera del suelo "+String(lecturaporcentaje)+"%");
    digitalWrite(D0, HIGH);
    //digitalWrite(2, HIGH);
    //digitalWrite(LED_BUILTIN, HIGH);
    delay(2000);
    digitalWrite(D0, LOW);
    //digitalWrite(2, LOW);
    //digitalWrite(LED_BUILTIN, LOW);
   }
   else if(lecturaporcentaje<30 && humedad>=10)
   {
    Serial.println("El suelo esta seco "+String(lecturaporcentaje)+"%");
   }
   else if(lecturaporcentaje<90 && humedad>=30)
   {
    Serial.println("El suelo esta humedo "+String(lecturaporcentaje)+"%");
   }
   else if(lecturaporcentaje>=90)
   {
    Serial.println("El sensor está en agua "+String(lecturaporcentaje)+"%");
   }
   int i = 1;
   String temperatura="";
   float suma=0;
   float promedio=0;
   float suma1=0;
   float promedio1=0;
   do
   {
     suma = suma + sensorT.readTemperature();
     suma1 = suma1 + Luxometro.GetLightIntensity();
     i++;
   }
   while(i<21);
   promedio = suma/20;
   promedio1 = suma1/20;
   temperatura = String(promedio,7);
   Serial.println("Luz(iluminancia): "+String(promedio1)+" lx");
   Serial.println("Temperatura: "+temperatura+" C°");
   static bool band=false;
   if(promedio1<25 and band==false)
   {
     band=true;
     for(int i=0; i<NUMPIXELS; i++)
     {
       pixels.setBrightness(30);
       pixels.setPixelColor(i, pixels.Color(255, 255, 255));
       pixels.show();
       delay(200);
     }
   }

   else if(promedio1>=25 and band==true)
   {
    band=false;
     for(int i=0; i<NUMPIXELS; i++)
     {
       pixels.setBrightness(10);
       pixels.setPixelColor(i, pixels.Color(255, 100, 0));
       pixels.show();
       delay(100);
     }
   }
   digitalWrite(5, LOW);
   delay(1000);
   digitalWrite(5, HIGH);
   delay(2000);

}
