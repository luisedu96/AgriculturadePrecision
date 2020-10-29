from flask import Flask, render_template, jsonify, request
import mysql.connector
import sqlite3
import time
import numpy as np
import pandas as pd
import dash
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime, date, timedelta
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import plotly.graph_objs as go

from appTIC import app

#grafica con los datos del dia (datos actuales)

def lectura():
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

    hoy=datetime.today()+timedelta(hours=int(longitudes[-1]/15))
    muestras_index = []
    temperaturanew = []
    humedadsuelonew = []
    humedadamnew = []
    timestampnew = []
    luxnew=[]
    longitudesnew=[]
    latitudesnew=[]
    altitudesnew=[]
    for lec in range(len(fechas)):
        fecha=datetime.strptime(fechas[lec],'%Y-%m-%d %H:%M:%S.%f')
        if ((fecha.day==hoy.day) and (fecha.year==hoy.year) and (fecha.month==hoy.month)):
         muestras_index.append(lec)
    long=0
    lati=0
    alti=0

    for n in muestras_index:
        temperaturanew=np.append(temperaturanew,temperaturas[n])
        luxnew=np.append(luxnew,cant_luz[n])
        humedadsuelonew=np.append(humedadsuelonew,humedad_s[n])
        humedadamnew=np.append(humedadamnew,humedad_a[n])
        timestampnew=np.append(timestampnew,fechas[n])
        latitudesnew=np.append(latitudesnew,latitudes[n])
        longitudesnew=np.append(longitudesnew, longitudes[n])
        altitudesnew=np.append(altitudesnew,altitudes[n])

    for lon in range(len(longitudesnew)):
        long=longitudesnew[lon]+long
        lati=latitudesnew[lon]+lati
        alti=altitudesnew[lon]+alti
    long=long/len(longitudesnew)
    lati=lati/len(altitudesnew)
    alti=alti/len(altitudesnew)

    informacion='Posición del invernadero: {:.5f} , {:.5f}     Altitud: {:.3f}msnm'.format(lati,long,alti)

    figuretem = go.Figure()
    figuretem.add_trace(go.Scatter(x=timestampnew, y=temperaturanew,
                 mode='lines',
                 text='Temperatura SENSOR 1',
                 line = dict(color='orange', width=4),
                 name='Temperatura ID:'+str(ids[0])))
    figuretem.add_trace(go.Scatter(x=timestampnew, y=temperaturanew,
                 mode='markers',
                 text='Temperatura SENSOR 1',
                 line = dict(color='#F96933', width=4),
                 name='Muestras sensados'))
    figuretem.update_layout(title='Gráfica de Temperatura',
                 xaxis_title='Fecha',
                 yaxis_title='Temperatura °C')
    figuretem.show()

    figurehum = go.Figure()
    figurehum.add_trace(go.Scatter(x=timestampnew, y=humedadsuelonew,
                 mode='lines',
                 text='Humedad del suelo '+str(ids[0]),
                 line = dict(color='#03A4FD', width=4),
                 name='Humedad del suelo ID:'+str(ids[0])))
    figurehum.add_trace(go.Scatter(x=timestampnew, y=humedadamnew,
                 mode='lines',
                 text='Humedad ambiente SENSOR '+str(ids[0]),
                 line = dict(color='#376456', width=4),
                 name='Humedad del ambiente ID:'+str(ids[0])))
    figurehum.update_layout(title='Gráfica de Humedad',
                 xaxis_title='Fecha',
                 yaxis_title='Humedad %')
    figurehum.show()

    figurel = go.Figure()
    figurel.add_trace(go.Scatter(x=timestampnew, y=luxnew,
                 mode='lines',
                 text='Luz SENSOR 1',
                 line = dict(color='#16C2CE', width=4),
                 name='Lux ID:'+str(ids[0])))
    figurel.add_trace(go.Scatter(x=timestampnew, y=luxnew,
                 mode='markers',
                 text='Lux SENSOR '+str(ids[0]),
                 line = dict(color='#14949D', width=4),
                 name='Muestras sensados'))
    figurel.update_layout(title='Gráfica de la cantidad de luz recibida',
                 xaxis_title='Fecha',
                 yaxis_title='Luz (Lux)')
    figurel.show()
    return figuretem, figurehum, figurel, informacion

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
informa='No se encontró información del invernadero'

layout = html.Div(style={'backgroundColor': '#EC9A48',},children=[
      html.H1(id='Title1',children='Datos del invernadero',style={'color':'#3A65A6','text-align':'center'}),
      html.Div('Datos del día'),
      html.Div(id='mensaje', style={"fontSize":"110%",'color':'#000000'}, children=informa),
      #dcc.DatePickerSingle(id='datefecha',date=datetime(2020, 10, 18, 0, 0, 0)),
      #html.Div('Elige la hora'),
      #dcc.Slider(id='hora',min=0,max=23,marks={i: '{} horas'.format(i) for i in range(24)},value=0),
      #html.Div(id='encontrar',children='Esperando fechas', style={'color':'#3A65A6'}),
      dbc.Row([
      dbc.Col(dcc.Graph(id='graficT',
           figure=figureT),width=3),
      dbc.Col(dcc.Graph(id='graficH',
           figure=figureH),width=3),
      dbc.Col(dcc.Graph(id='graficlux',
           figure=figurelux),width=3),], className = "mb-4",),
      html.Button('Actualizar', id='button')])

@app.callback([Output('graficT','figure'),Output('graficH','figure'),Output('graficlux','figure'),Output('mensaje','children')],[Input('button', 'n_clicks')])
def update_output(n_clicks):
    mensaje='Gráfica Actualizado el: '+str(datetime.now())
    if (n_clicks):
       actual=lectura()
    else:
       actual=lectura()
    mensaje=actual[3]+' '+mensaje
    return actual[0],actual[1],actual[2],mensaje

