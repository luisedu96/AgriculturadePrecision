#include <TinyGPS++.h> 
#include <SoftwareSerial.h>
#include <ClosedCube_HDC1080.h>
#include <Adafruit_NeoPixel.h>
#include <BH1750FVI.h>
#include <Wire.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define RX 18
#define TX 17
#define PIN 16 //leds
#define NUMPIXELS 12 //numero leds
#define D0 23 //motor

const int sensorPin = A0; //sensor humedad suelo
const char* ssid = "MARTINEZ_EXT";
const char* password = "71314912";
int id = 1001;

//poner la direccion IP del servidor
const char* server = "54.91.180.147";

static float suma = 0, promedio = 0;
double t_sleep = 10;//segundos
static int estado = 1;
bool precision = false, decodificacion = false;

static String temperatura = "", cant_luz = "", humedad_amb = "", humedad_suelo = "", latitud = "", longitud = "", fecha = "", hora="", Trama = "", altitud = "", actuadores="";
static int usuario = 4569;
WiFiClient client; //cliente wifi para POST
TinyGPSPlus GPSL70; //gps
SoftwareSerial ssGPS(TX, RX); //gps comunicacion
ClosedCube_HDC1080 sensor; //sensor temperatura y humedad
BH1750FVI luxometro(BH1750FVI::k_DevModeContLowRes); //sensor de luz
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);  //leds
HTTPClient http; //cliente http GET

void setup()
{
 pinMode(5, OUTPUT);
 digitalWrite(5, HIGH);
 Serial.begin(9600);
 pixels.begin();
 ssGPS.begin(9600);
 sensor.begin(0x40);
 luxometro.begin();
 Serial.println();
 WiFi.begin(ssid, password);
 Serial.println();
 Serial.println("Iniciando...");
 Serial.print("Connecting to ");
 Serial.println(ssid);
 WiFi.begin(ssid, password);

 while (WiFi.status() != WL_CONNECTED)
 {
  delay(500);
  Serial.print(".");
  digitalWrite(5, LOW);
  delay(100);
  digitalWrite(5, HIGH);
  residuos();//lee las tramas nmea acumulados en el puerto serial
 }

 Serial.println("");
 Serial.println("WiFi connected");
 //digitalWrite(5, LOW);
}

void loop()
{
  //actuadores="0;0";
  Trama = "";
  double inicio = millis();
  switch (estado)
  {
    case 1:
          decodificar_nmea();//leer la trama nmea a travez de la biblioteca tinyGPSplus
          if(decodificacion) estado = 2;//decodificacion es de tipo booleano, si se hizo el proceso de leer la trama nmea éste será verdadero y pasará al estado siguiente. 
          else estado=1;//si decodificacion es falso se devolverá a1 estado 1.
          decodificacion = false;
          residuos();       
    break;
    case 2:
          confiabilidad_Datos();//evalúa la precision de los datos leidos del gps. 
          if(precision)//precision es de tipo booleano, si la evalucion es corecta precision es verdadero pasa al estado 3  
          {
            estado=3;
            Serial.println("Datos más precisos posibles");
          }
          else estado=1;// si la precision es falso se devuleve al estdo 1.
          precision = false;
          residuos();
    break;
    case 3:
          Temperatura();//capta informacion de temperatura del sensor y las convierte en datos.
          estado=4;
          residuos();
    break;
    case 4:
          Humedad_amb();//capta informacion de humedad del sensor y la convierte en dato
          Humedad_suelo();
          estado=5;
          residuos();
    break;
    case 5:
          Posicion();//toma los datos leidos por el tinygpsplus y seleciona latitud y longitud
          estado=6;
          residuos();
    break;
    case 6:
          Luxometro();
          Fecha();//toma los datos leidos por el tinygpsplus y seleciona la hora
          estado=7;
          residuos();
    break;
    case 7:
          Hora();//toma los datos leidos por el tinygpsplus y selecciona la fecha
          estado=8;
          residuos();
    break;
    case 8:
          Armar_Trama();
          Enviar();//toma todos los datos obtenidos (temperatura, humedad, posicion, fecha, hora) y arma la trama
          httpRequest(); //realiza un GET y espera respuesta para activar los actuadores
          residuos();
          estado=9;
    break;
    case 9:
          actuar();
          double tiempo_encendido = millis()-inicio;
          Serial.print("Tiempo ecendido: ");Serial.println(tiempo_encendido);
          estado=1;
          residuos(); //delay smart
          double tiempo_dormido=t_sleep*1000-tiempo_encendido;
          dormir(tiempo_dormido);//entra en el modo deepsleep para ahorrar energía.
    break;
  }
}

void decodificar_nmea()//codifica la trama nmea con la libreri tinygpsplus
{
  while (ssGPS.available()>0)
  {
    if(GPSL70.encode(ssGPS.read())) decodificacion=true;
    //LED ROJO PARA CONFIRMACION
  }
}

void Posicion()//tomar latitud y longitud la lectura que hizo tinygpsplus y convierte en grados minutos y segundos
{
  latitud = "";
  longitud = "";
  float LA = GPSL70.location.lat(), LO = GPSL70.location.lng(), ALT = GPSL70.altitude.meters();
  latitud = String(LA,7);
  longitud = String(LO,7);
  altitud = String(ALT,7);
}

void Fecha()
{
  fecha="";
  int d = GPSL70.date.day(), m = GPSL70.date.month(), y = GPSL70.date.year();
  fecha.concat(d);fecha.concat('/');fecha.concat(m);fecha.concat('/');fecha.concat(y);
  //Serial.print("Fecha: ");Serial.println(fecha);
}

void Hora()
{
  hora="";
  int h = GPSL70.time.hour(), m = GPSL70.time.minute(), s = GPSL70.time.second();
  int dif = int(GPSL70.location.lng()/15);
  if(h==0) h=24;
  h=h+dif;
  if(h<10)
  {
    hora.concat('0');hora.concat(String(h));
  }
  else hora.concat(String(h));
  hora.concat('-');
  if(m<10)
  {
    hora.concat('0');hora.concat(String(m));
  }
  else hora.concat(m);
  hora.concat('-');
  if(s<10)
  {
    hora.concat('0');hora.concat(s);
  }
  else hora.concat(s);
  fecha.concat(' ');
  fecha.concat(hora);
  Serial.print("Fecha: ");Serial.println(fecha);
}

void Temperatura()
{ 
  temperatura = "";
  int i = 1;
  do
  {
    suma = suma + sensor.readTemperature();
    i++;
  }
  while(i<21);
  promedio=suma/20;
  temperatura = String(promedio,7);
  promedio = 0;
  suma=0;
}

void Humedad_amb()
{ 
  humedad_amb="";
  int i = 1;
  do
  {
    suma = suma + sensor.readHumidity();
    i++;
  }
  while(i<21);
  promedio=suma/20;
  humedad_amb = String(promedio,7);
  promedio=0;
  suma=0;
}

void Humedad_suelo()
{
  humedad_suelo="";
  int i = 1;
  do
  {
    suma = suma + analogRead(sensorPin);
    i++;
  }
  while(i<21);
  promedio=suma/20;
  float lecturaporcentaje = map(promedio, 4095, 2430, 0, 100);
  humedad_suelo = String(lecturaporcentaje);
  promedio=0;
  suma=0;
}

void Luxometro()
{
  cant_luz="";
  int i = 1;
  do
  {
    suma = suma + luxometro.GetLightIntensity();
    i++;
  }
  while(i<21);
  promedio=suma/20;
  cant_luz = String(promedio);
  promedio=0;
  suma=0;
}

void confiabilidad_Datos()//analiza la preciion de los datos del gps para tener una mayor precision. 
{
  if(GPSL70.location.isValid() && GPSL70.altitude.isValid() && GPSL70.date.isValid()
  && GPSL70.satellites.isValid())
  {
    precision = true;
    //encender led rojo
  }
  else
  {
    Serial.println("precision baja");
    precision = false;
  }
}

void Armar_Trama()
{
  Trama = "";
  Serial.print ("Trama creada: ");
  Trama = String("id="+String(id)+"; Usuario="+String(usuario)+"; fecha="+'"'+fecha+'"'+"; temperatura="+temperatura+"; humedad ambiente="+humedad_amb+"; humedad suelo="+humedad_suelo+"; latitud="+latitud +"; longitud="+longitud+"; altitud="+altitud+"; luz="+cant_luz);
  Serial.println(Trama);
}

void dormir(double t)
{
  Serial.println("Modo sleep");
  Serial.println("-----------------------------------------------------");
  //ESP.deepSleep(t_sleep*1000000, WAKE_RF_DISABLED);
  delay(t);
}

void residuos()
{
  while(ssGPS.available()>0)
  {
    GPSL70.encode(ssGPS.read());
  }
}

void Enviar()
{
 String PostData = "";
 Serial.println("datos para enviar");
 PostData = Trama; //String("id="+String(id)+"; temperatura="+String(temperatura,7)+"; longitud="+String(longitud,7)+"; latitud="+String(latitud,7));
 Serial.println(PostData);
 if ( client.connect(server,80))
 {
  Serial.println("conectado");
  client.print("POST /datos HTTP/1.1\n");
  // poner la direccion IP del servidor 
  client.print("Host: 54.91.180.147\n");
  client.println("User-Agent: Arduino/1.0");
  client.println("Connection: close");
  client.println("Content-Type: application/x-www-form-urlencoded;");
  client.print("Content-Length: ");
  client.println(PostData.length());
  client.println();
  client.println(PostData);
  client.stop();
  //encender led verde
 }
 else
 {
  Serial.println("error de conexion");
 }
}

void httpRequest() //realiza un GET y activa los actuadores dependeiendo de la informacion de la trama respuesta del GET 
{
  if ((WiFi.status() == WL_CONNECTED)) 
  { //Check the current connection status
    http.begin("http://54.91.180.147/pedir"); //Specify the URL
    int httpCode = http.GET();//Make the request
    if (httpCode > 0)
    { //Check for the returning code
        String payload = http.getString();
        actuadores=payload;
        Serial.println(httpCode);
        Serial.println(payload);
    }
    else 
    {
      Serial.println("Error on HTTP request");
    }
    http.end(); //Free the resources
  }
  //delay(500);
}

void actuar()
{
  //String motor = getValue(actuadores,';', 0);
  String luz = getValue(actuadores, ';', 1);
  //Serial.println(motor+luz);
  if(luz=="1")
  {
    for(int i=0; i<NUMPIXELS; i++)
     {
       pixels.setBrightness(30);
       pixels.setPixelColor(i, pixels.Color(255, 255, 255));
       pixels.show();
       delay(100);
     }
  }
  else if(luz=="2")
  { 
    Serial.println("Luz led");
  }
  else if(luz=="3")
  {
    for(int i=0; i<NUMPIXELS; i++)
     {
       pixels.setBrightness(10);
       pixels.setPixelColor(i, pixels.Color(0, 0, 0));
       pixels.show();
       delay(100);
     }
  }
}

String getValue(String data, char separator, int index) //split()
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
