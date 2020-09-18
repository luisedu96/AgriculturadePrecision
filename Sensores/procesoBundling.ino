#include <TinyGPS++.h> 
#include <SoftwareSerial.h>
#include <ClosedCube_HDC1080.h>
#include <Wire.h>
#include <ESP8266WiFi.h>

#define ESP82_GPS_RX 2
#define ESP82_GPS_TX 0

const char* ssid = "TIGO-B6F1";
const char* password = "2NJ557301874";
//poner la direccion IP del servidor
const char* server = "54.82.192.174";
int id = 1001;

static float suma = 0, promedio = 0;
double t_sleep = 60;//segundos
static int estado = 1;
bool precision = false, decodificacion = false;

static String temperatura = "", humedad = "", latitud = "", longitud = "", fecha = "", hora="", Trama = "";

WiFiClient client;
TinyGPSPlus GPSL70;
SoftwareSerial ssGPS(ESP82_GPS_RX, ESP82_GPS_TX);
ClosedCube_HDC1080 sensor;

void setup()
{
 Serial.begin(9600);
 ssGPS.begin(9600);
 sensor.begin(0x40);
 Serial.println();
 WiFi.begin(ssid, password);
 Serial.println();
 Serial.println("Iniciando...");
 Serial.print("Connecting to ");
 Serial.println(ssid);

 WiFi.begin(ssid, password);

 while (WiFi.status() != WL_CONNECTED) {

   delay(500);

   Serial.print(".");
  residuos();//lee las tramas nmea acumulados en el puerto serial
 }

 Serial.println("");
 Serial.println("WiFi connected");
}
void loop()
{
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
          Humedad();//capta informacion de humedad del sensor y la convierte en dato
          estado=5;
          residuos();
    break;
    case 5:
          Posicion();//toma los datos leidos por el tinygpsplus y seleciona latitud y longitud
          estado=6;
          residuos();
    break;
    case 6:
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
          residuos();
          estado=9;
    break;
    case 9:
          double tiempo_encendido = millis()-inicio;
          Serial.print("Tiempo ecendido: ");Serial.println(tiempo_encendido);
          estado=1;
          residuos();
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
  }
}

void Posicion()//tomar latitud y longitud la lectura que hizo tinygpsplus y convierte en grados minutos y segundos
{
  latitud = "";
  longitud = "";
  float LA = GPSL70.location.lat(), LO = GPSL70.location.lng();
  latitud = String(LA,7);
  longitud = String(LO,7);
}

void Fecha()
{
  fecha="";
  int d = GPSL70.date.day(), m = GPSL70.date.month(), y = GPSL70.date.year();
  fecha.concat(d);fecha.concat('/');fecha.concat(m);fecha.concat('/');fecha.concat(y);
  Serial.print("Fecha: ");Serial.println(fecha);
}

void Hora()
{
  hora="";
  int h = GPSL70.time.hour(), m = GPSL70.time.minute(), s = GPSL70.time.second();
  if(h<10)
  {
    hora.concat('0');hora.concat(String(h));
  }
  else hora.concat(String(h));
  hora.concat(':');
  if(m<10)
  {
    hora.concat('0');hora.concat(String(m));
  }
  else hora.concat(m);
  hora.concat(':');
  if(s<10)
  {
    hora.concat('0');hora.concat(s);
  }
  else hora.concat(s);
  hora.concat("GTM"); hora.concat(String(int(GPSL70.location.lng()/15)));Serial.print("Hora: ");Serial.println(hora);
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
  i=1;
}

void Humedad()
{ 
  humedad="";
  int i = 1;
  do
  {
    suma = suma + sensor.readHumidity();
    i++;
  }
  while(i<21);
  promedio=suma/20;
  humedad = String(promedio,7);
  promedio=0;
  suma=0;
  i=1;
}

void confiabilidad_Datos()//analiza la preciion de los datos del gps para tener una mayor precision. 
{
  if(GPSL70.location.isValid() && GPSL70.date.isValid() && GPSL70.date.isValid() 
  && GPSL70.satellites.isValid())
  {
    precision = true;
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
  Trama = String("id="+String(id)+"; temperatura="+temperatura+"; humedad="+humedad+"; latitud="+latitud +"; longitud="+longitud);
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
  client.print("Host: 54.82.192.174\n");
  client.println("User-Agent: Arduino/1.0");
  client.println("Connection: close");
  client.println("Content-Type: application/x-www-form-urlencoded;");
  client.print("Content-Length: ");
  client.println(PostData.length());
  client.println();
  client.println(PostData);
 }
 else
 {
  Serial.println("error de conexion");
 }
}
