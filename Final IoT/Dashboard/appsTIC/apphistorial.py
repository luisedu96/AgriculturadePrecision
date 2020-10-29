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

#apphistorial retorna los gráficos según la hora y el dia que elija el usuario del hitorial de la base de datos. 
def lectura2():
  midb = mysql.connector.connect(
    host="invernaderofinal.crjll9jlhd3b.us-east-1.rds.amazonaws.com",
    user="admin",
    password="123456789",
    database="invernadero"
  )

  #app = dash.Dash(__name__, server=server, routes_pathname_prefix='/miinvernadero/')
  cursor = midb.cursor()
  cursor.execute("SELECT * FROM datosTIC")
  usuarios=[]
  ids=[]
  fechas = []
  temperaturas = []
  humedad_a = []
  humedad_s = []
  latitudes = []
  longitudes = []
  altitudes = []
  cant_luz = []
  resultado = cursor.fetchall()

  for x in resultado:
      usuarios.append(x[0])
      ids.append(x[1])
      fechas.append(x[2])
      temperaturas.append(x[3])
      humedad_a.append(x[4])
      humedad_s.append(x[5])
      latitudes.append(x[6])
      longitudes.append(x[7])
      altitudes.append(x[8])
      cant_luz.append(x[9])
  return ids, fechas,temperaturas,humedad_a,humedad_s,latitudes,longitudes,altitudes,cant_luz

layout = html.Div(style={'backgroundColor': '#AAE4A7',},children=[
   html.H1(id='Title1',children='Datos del invernadero',style={'color':'#3A65A6','text-align':'center'}),
   html.H2('Elige la fecha a consultar'),
   dcc.DatePickerSingle(id='datefecha',date=datetime(2020, 10, 18, 0, 0, 0)),
   html.H3('Elige la hora'),
   dcc.Slider(id='hora',min=0,max=23,marks={i: '{} horas'.format(i) for i in range(24)},value=0),
   html.Div(id='encontrar',children='Esperando fechas...', style={"fontSize":"110%",'color':'#083E76'}),
   html.Div(id='info', style={"fontSize":"110%",'color':'#000000'}),
   html.Div(children=[html.Div(dcc.Graph(id='graficaT',
        figure={
            'data': [
                {'x': [], 'y': [], 'type': 'scatter', 'name': 'Temperatura sensor 1'},
            ],
            'layout': {
               'title': 'Gráfica de datos de Temperatura'
            }
        }),className='col s12 m6 l6'),
        html.Div(dcc.Graph(id='graficaH',
        figure={
            'data': [
                {'x': [], 'y': [], 'type': 'scatter', 'name': 'Humedad sensor 1'},
            ],
            'layout': {
                'title': 'Gráfica de datos de Humedad'
            }
        }), className='col s12 m6 l6'),
        html.Div(dcc.Graph(id='graficaluz',
        figure={
            'data': [
                {'x': [], 'y': [], 'type': 'scatter', 'name': 'Humedad sensor 1'},
            ],
            'layout': {
                'title': 'Gráfica de la cantidad de luz recibida'
            }
        }), className='col s12 m6 l6')], className='row')])

@app.callback(Output('encontrar','children'),[Input('datefecha','date'),Input('hora','value')])
def print_index(datefecha,hora):
   actual=lectura2()
   idsis=actual[0]
   fech=actual[1]
   tempe=actual[2]
   humeam=actual[3]
   humesu=actual[4]
   lats=actual[5]
   lons=actual[6]
   alts=actual[7]
   canluz=actual[8]
   fecha_elegida=datetime.strptime(datefecha.split('T')[0],'%Y-%m-%d')+timedelta(hours=hora,minutes=0,seconds=0)
   band=True
   mensaje=' '
   muestras_index = []
   for lec in range(len(fech)):
       fecha=datetime.strptime(fech[lec],'%Y-%m-%d %H:%M:%S.%f')
       if ((fecha.day==fecha_elegida.day) and (fecha.year==fecha_elegida.year) and (fecha.month==fecha_elegida.month) and (fecha.hour==fecha_elegida.hour)):
           band=False
           muestras_index.append(lec)
           mensaje='Se muestra datos entre {} y {} del {}. El número de muestras es {}'.format(str(fecha_elegida.time()), str((fecha_elegida+timedelta(hours=1)).time()), str(fecha_elegida).split(' ')[0], len(muestras_index))
   if band:
       mensaje='Error, No se encontraron datos en la fecha elegida'
   return mensaje

@app.callback([Output('graficaT','figure'),Output('graficaH','figure'), Output('graficaluz','figure'), Output('info','children')],[Input('datefecha','date'),Input('hora','value')])
def print_index(datefecha,hora):
   actual=lectura2()
   idsis=actual[0]
   fech=actual[1]
   tempe=actual[2]
   humeam=actual[3]
   humesu=actual[4]
   lats=actual[5]
   lons=actual[6]
   alts=actual[7]
   canluz=actual[8]
   fecha_elegida=datetime.strptime(datefecha.split('T')[0],'%Y-%m-%d')+timedelta(hours=hora,minutes=0,seconds=0)
   band=True
   #muestra=0
   muestras_index = []
   temperaturanew = []
   humedadsuelonew = []
   humedadamnew = []
   timestampnew = []
   luxnew=[]
   longitudesnew=[]
   latitudesnew=[]
   altitudesnew=[]
   for lec in range(len(fech)):
       fecha=datetime.strptime(fech[lec],'%Y-%m-%d %H:%M:%S.%f')
       if ((fecha.day==fecha_elegida.day) and (fecha.year==fecha_elegida.year) and (fecha.month==fecha_elegida.month) and (fecha.hour==fecha_elegida.hour)):
           band=False
           muestras_index.append(lec)

   if band:
       figureT={
            'data': [
                {'x': [], 'y': [], 'type': 'scatter', 'name': 'Temperatura sensor 1'},
            ],
            'layout': {
                'title': 'Gráfica de datos de Temperatura'
            }
        }
       figureH={
            'data': [
               {'x': [], 'y': [], 'type': 'scatter', 'name': 'Temperatura sensor 1'},
            ],
            'layout': {
                'title': 'Gráfica de datos de Humedad'
            }
        }
       figurelux={
            'data': [
               {'x': [], 'y': [], 'type': 'scatter', 'name': 'Temperatura sensor 1'},
            ],
            'layout': {
                'title': 'Gráfica de la cantidad de luz recibida'
            }
        }
       informacion='No se encontró información del invernadero'

   elif (not band):
       long=0
       lati=0
       alti=0
       for n in muestras_index:
           temperaturanew=np.append(temperaturanew,tempe[n])
           luxnew=np.append(luxnew,canluz[n])
           humedadsuelonew=np.append(humedadsuelonew,humesu[n])
           humedadamnew=np.append(humedadamnew,humeam[n])
           timestampnew=np.append(timestampnew,fech[n])
           latitudesnew=np.append(latitudesnew,lats[n])
           longitudesnew=np.append(longitudesnew, lons[n])
           altitudesnew=np.append(altitudesnew,alts[n])

       for lon in range(len(longitudesnew)):
           long=longitudesnew[lon]+long
           lati=latitudesnew[lon]+lati
           alti=altitudesnew[lon]+alti
       long=long/len(longitudesnew)
       lati=lati/len(altitudesnew)
       alti=alti/len(altitudesnew)
       informacion='Posición del invernadero: {:.5f} , {:.5f}     Altitud: {:.3f}msnm'.format(lati,long,alti)
       figureT = go.Figure()
       figureT.add_trace(go.Scatter(x=timestampnew, y=temperaturanew,
                    mode='lines',
                    text='Temperatura SENSOR 1',
                    line = dict(color='orange', width=4),
                    name='Temperatura ID:'+str(idsis[0])))
       figureT.add_trace(go.Scatter(x=timestampnew, y=temperaturanew,
                    mode='markers',
                    text='Temperatura SENSOR 1',
                    line = dict(color='#F96933', width=4),
                    name='Muestras sensados'))
       figureT.update_layout(title='Gráfica de Temperatura',
                    xaxis_title='Fecha',
                    yaxis_title='Temperatura °C')
       figureT.show()

       figureH = go.Figure()
       figureH.add_trace(go.Scatter(x=timestampnew, y=humedadsuelonew,
                    mode='lines',
                    text='Humedad del suelo '+str(idsis[0]),
                    line = dict(color='#03A4FD', width=4),
                    name='Humedad del suelo ID:'+str(idsis[0])))
       figureH.add_trace(go.Scatter(x=timestampnew, y=humedadamnew,
                    mode='lines',
                    text='Humedad ambiente SENSOR '+str(idsis[0]),
                    line = dict(color='#376456', width=4),
                    name='Humedad del ambiente ID:'+str(idsis[0])))
       figureH.update_layout(title='Gráfica de Humedad',
                    xaxis_title='Fecha',
                    yaxis_title='Humedad %')
       figureH.show()

       figurelux = go.Figure()
       figurelux.add_trace(go.Scatter(x=timestampnew, y=luxnew,
                    mode='lines',
                    text='Luz SENSOR 1',
                    line = dict(color='#16C2CE', width=4),
                    name='Lux ID:'+str(idsis[0])))
       figurelux.add_trace(go.Scatter(x=timestampnew, y=luxnew,
                    mode='markers',
                    text='Lux SENSOR '+str(idsis[0]),
                    line = dict(color='#14949D', width=4),
                    name='Muestras sensados'))
       figurelux.update_layout(title='Gráfica de la cantidad de luz recibida',
                    xaxis_title='Fecha',
                    yaxis_title='Luz (Lux)')
       figureH.show()
   return figureT, figureH, figurelux, informacion
