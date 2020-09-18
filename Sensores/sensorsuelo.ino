const int sensorPin = A0;

void setup() {
   Serial.begin(9600);
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
   Serial.println(lecturaporcentaje);
  
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
   delay(2000);
}
