#include <Wire.h>
#include <ClosedCube_HDC1080.h>
#include <BH1750FVI.h>
//#include <SoftwareSerial.h>

const int sensorPin = A0;

ClosedCube_HDC1080 sensorT;
BH1750FVI Luxometro(BH1750FVI::k_DevModeContLowRes);
void setup() {
   Serial.begin(9600);
   sensorT.begin(0x40);
   Luxometro.begin(0x23);
}

void loop() 
{  
   float humedad = 0;
   int num=20;
   while(num!=0)
   {
    float suma = analogRead(sensorPin);
    humedad = humedad+suma;
    num=num-1;
   }
   humedad=humedad/20;
   float lecturaporcentaje = map(humedad, 1024, 530, 0, 100);
   Serial.println(humedad);
   //Serial.println(lecturaporcentaje);
  
   if(lecturaporcentaje<10)
   {
    Serial.println("El sensor está desconectado o fuera del suelo "+String(lecturaporcentaje)+"%"); 
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
   delay(2000);
}
