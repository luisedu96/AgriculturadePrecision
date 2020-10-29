
from flask import Flask, render_template, jsonify, request, redirect
import mysql.connector
import sqlite3
import numpy as np
import pandas as pd
import dash
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime, date, time, timedelta
import dash_core_components as dcc
import plotly.graph_objs as go

from appTIC import app, server
from appsTIC import appactual, apphistorial

#recolecta informacion y las almacena en la base de datos
#redirige a las graficas(htorico de datos o los datos del dia)

midb = mysql.connector.connect(
  host="invernaderofinal.crjll9jlhd3b.us-east-1.rds.amazonaws.com",
  user="admin",
  password="123456789",
  database="invernadero"
)

@server.route('/')
def inicio():
   return "hola mundo",200

@server.route('/visualizacion')
def visualizacion():
     cursor = midb.cursor()
     cursor.execute("SELECT * FROM datosTIC")
     resultado = cursor.fetchall()
     for x in resultado:
       print(x)
     return "codigo para visualizar datos",201

#alamacena datos en la base de datos
@server.route('/datos',methods=['POST'])
def recibirdatos():
  valores = request.values
  print(str(valores))
  a = str(request.values.get('id'))
  d1 = a.split(';')[0] #id
  du = a.split(';')[1].split('=')[1] #usuario
  #d2 = "\""+str(datetime.today())+"\""  #a.split(';')[2].split('=')[1]
  d3 = a.split(';')[3].split('=')[1] #temperatura
  d4 = a.split(';')[4].split('=')[1] #humedad ambiente
  d5 = a.split(';')[5].split('=')[1] #humedad suelo
  d6 = a.split(';')[6].split('=')[1] #latitud
  d7 = a.split(';')[7].split('=')[1] #longitud
  d8 = a.split(';')[8].split('=')[1] #altitud
  d9 = a.split(';')[9].split('=')[1] #luz
  d2 = "\""+str(datetime.today()+timedelta(hours=-5)+"\"" #fecha 
  cur = midb.cursor()
  cur.execute("INSERT INTO datosTIC VALUES("+du+","+d1 +","+d2+"," +d3 +","+d4 +","+d5 +","+d6 +","+d7 +","+d8 +","+d9 +")")
  midb.commit()
  return "OK",200

#responde con la informacion para la activacion de los actuadores
@server.route('/pedir',methods=['GET'])
def actuar():
   midb = mysql.connector.connect(
     host="invernaderofinal.crjll9jlhd3b.us-east-1.rds.amazonaws.com",
     user="admin",
     password="123456789",
     database="invernadero"
   )

   cursor = midb.cursor()
   cursor.execute("SELECT * FROM datosTIC")
   usuario=0
   id=0
   fecha = 0
   temperatura = 0
   humedad_am = 0
   humedad_su = 0
   latitud = 0
   longitud = 0
   altitud = 0
   cant_luz = 0
   resultado = cursor.fetchall()
   print("solucitud del arduino")
   for x in resultado:
       usuario=x[0]
       id=x[1]
       fecha=datetime.strptime(x[2],'%Y-%m-%d %H:%M:%S.%f')
       temperatura=x[3]
       humedad_am=x[4]
       humedad_su=x[5]
       latitud=x[6]
       longitud=x[7]
       altitud=x[8]
       cant_luz=x[9]
   comando1='0'
   comando2='0'
   if ((temperatura>20 or humedad_am<75) and humedad_su<80): comando1="1"
   if ((fecha.hour>16 or humedad_am<75) and humedad_su<80):comando1="1"
   if (cant_luz<10 and fecha.hour>=7 and fecha.hour<=18):comando2="1"
   if (cant_luz<10 and fecha.hour>18): comando2="3"
   if (cant_luz<10 and fecha.hour<7): comando2="2"
   if (cant_luz>=10 and cant_luz<=250): comando2="2"
   if (cant_luz>250):comando2="3"
   trama=comando1+";"+comando2
   return trama, 200

#metodo para la app movil
@server.route('/movildata', methods=['POST'])
def movil_data():
   midb = mysql.connector.connect(
     host="invernaderofinal.crjll9jlhd3b.us-east-1.rds.amazonaws.com",
     user="admin",
     password="123456789",
     database="invernadero"
   )

   cursor = midb.cursor()
   cursor.execute("SELECT * FROM datosTIC")
   usuario=0
   id=0
   fecha = 0
   temperatura = 0
   humedad_am = 0
   humedad_su = 0
   latitud = 0
   longitud = 0
   altitud = 0
   cant_luz = 0
   resultado = cursor.fetchall()
   print("solucitud del arduino")
   for x in resultado:
       usuario=x[0]
       id=x[1]
       fecha=datetime.strptime(x[2],'%Y-%m-%d %H:%M:%S.%f')
       temperatura=x[3]
       humedad_am=x[4]
       humedad_su=x[5]
       latitud=x[6]
       longitud=x[7]
       altitud=x[8]
       cant_luz=x[9]
   trama=""
   valores = request.values
   print(str(valores))
   a = str(request.values.get('user'))
   user = a.split(';')[0]
   band=user.isdigit()
   if (band and int(user)==usuario):
      t1="No se realizó ninguna acción en el riego."
      t2=" No se realixó ninguna acción para compensar la luz recibida."
      if ((temperatura>20 or humedad_am<75) and humedad_su<80):
         t1="Se Regó por falta de humedad y elevada temperatura. "
      if ((fecha.hour>16 or humedad_am<75) and humedad_su<80):
         t1="Riego programado en la noche tomando en cuenta la humedad. "
      if (cant_luz<10 and fecha.hour>=7 and fecha.hour<=18):
         t2="Escasa luz recibida, se encenderon los leds. "
      if (cant_luz<10 and fecha.hour>18):
         t2="La noche es muy importante para las plantas, ya que es entonces cuando metabolizan la energía almacenada durante el dia. Leds off. "
      if (cant_luz<10 and fecha.hour<7):
         t2="La noche es muy importante para las plantas, ya que es entonces cuando metabolizan la energía almacenada durante el dia. Leds off. "
      if (cant_luz>=10 and cant_luz<=250):
         t2="Escasa luz recibida, se encendieron los leds. "
      if (cant_luz>250):
         t2="Muy buena luz recibida, no es necesario encender los leds. "
      trama=str(humedad_su)+";"+str(humedad_am)+";"+str(cant_luz)+";"+str(id)+";"+str(altitud)+" msnm"+";"+t1+t2
   else:
      trama="NaN;NaN;NaN;NaN;NaN;Usuario no registrado, error en formato."
   return trama

#app = dash.Dash(__name__, server=server, routes_pathname_prefix='/index/')
app.layout = html.Div(id='cambio', style={'backgroundColor': '#A7C0E4',}, children=[
   html.H1(id='Title1',children='Bienvenido',style={'color':'#3A65A6','text-align':'center'}),
   html.H2('Elige una opción'),
   #html.Button('Histórico de datos', id='hist', n_clicks=0),
   #html.Button('Datos de hoy', id='hoy', n_clicks=0),
   dcc.Location(id='url', refresh=False),
   dcc.Link('histórico de datos', href='/apps/apphistorial', style={"fontSize":"150%","text-align":"center"}),
   html.Br(),
   dcc.Link('Datos sensados actuales', href='/apps/appactual', style={"fontSize":"150%",'text-align':'center'}),
   html.Div(id='page-content', children=[])
   ])

#dependencias para la eleccion de las graficas
@app.callback(Output('cambio', 'children'),[Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/apphistorial':
        return apphistorial.layout
    elif pathname == '/apps/appactual':
        return appactual.layout
    elif pathname == '/':
        return app.layout
    else:
        return "404 Page Error! Please choose a link"


if (__name__ == '__main__'):
  app.run_server(debug=True, host='0.0.0.0', port=80)
