import numpy as np
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
from datetime import datetime, date, time, timedelta
import sqlite3

db = "mibasededatos.db"
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("SELECT * FROM registro")
latitud=[]
longitud=[]
temperatura = []
humedad = []
timestamp = []
fechas = []
numero = 0
for fila in cur.execute("SELECT * FROM registro"):
  timestamp.append(fila[1])
  temperatura.append(fila[2])
  humedad.append(fila[3])
  latitud.append(fila[4])
  longitud.append(fila[5])

for t in timestamp:
  f=str(datetime.strptime(t,'%Y-%m-%d %H:%M:%S')+timedelta(hours=-5))
  fechas.append(f)

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(id='Title1',children='Datos enviados desde el nodeMCU',style={'color':'#3A65A6','text-align':'center'}),
    html.Div('Elige la fecha a consultar'),
    dcc.DatePickerSingle(id='datefecha',date=datetime(2020, 9, 6, 0, 0, 0)),
    html.Div('Elige la hora'),
    dcc.Slider(id='hora',min=0,max=23,marks={i: '{} horas'.format(i) for i in range(24)},value=0),
    html.Div(id='encontrar',children='Esperando fechas', style={'color':'#3A65A6'}),
    dcc.Graph(id='graficaT',
        figure={
            'data': [
                {'x': [], 'y': [], 'type': 'scatter', 'name': 'Temperatura sensor 1'},
            ],
            'layout': {
                'title': 'Gráfica de datos de Temperatura'
            }
        }),
    dcc.Graph(id='graficaH',
        figure={
            'data': [
                {'x': [], 'y': [], 'type': 'scatter', 'name': 'Humedad sensor 1'},
            ],
            'layout': {
                'title': 'Gráfica de datos de Humedad'
            }
        })
   ])

@app.callback(dash.dependencies.Output('encontrar','children'),[dash.dependencies.Input('datefecha','date'),dash.dependencies.Input('hora','value')])
def print_index(datefecha,hora):
   fecha_elegida=datetime.strptime(datefecha.split('T')[0],'%Y-%m-%d')+timedelta(hours=hora,minutes=0,seconds=0)
   band=True
   mensaje=' '
   muestras_index = []
   for lec in range(len(fechas)):
       fecha=datetime.strptime(fechas[lec],'%Y-%m-%d %H:%M:%S')
       if ((fecha.day==fecha_elegida.day) and (fecha.year==fecha_elegida.year) and (fecha.month==fecha_elegida.month) and (fecha.hour==fecha_elegida.hour)):
           band=False
           muestras_index.append(lec)
           mensaje='Se muestra datos entre {} y {} del {}. El número de muestras es {}'.format(str(fecha_elegida.time()), str((fecha_elegida+timedelta(hours=1)).time()), str(fecha_elegida).split(' ')[0], len(muestras_index))
   if band:
       mensaje='Error, No se encontraron datos en la fecha elegida'
   return mensaje

@app.callback([dash.dependencies.Output('graficaT','figure'),dash.dependencies.Output('graficaH','figure')],[dash.dependencies.Input('datefecha','date'),dash.dependencies.Input('hora','value')])
def print_index(datefecha,hora):
   fecha_elegida=datetime.strptime(datefecha.split('T')[0],'%Y-%m-%d')+timedelta(hours=hora,minutes=0,seconds=0)
   band=True
   #muestra=0
   muestras_index = []
   temperaturanew = []
   humedadnew = []
   timestampnew = []
   for lec in range(len(fechas)):
       fecha=datetime.strptime(fechas[lec],'%Y-%m-%d %H:%M:%S')
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

   elif (not band):
       for n in muestras_index:
           temperaturanew=np.append(temperaturanew,temperatura[n])
           humedadnew=np.append(humedadnew,humedad[n])
           timestampnew=np.append(timestampnew,fechas[n])

       figureT = go.Figure()
       figureT.add_trace(go.Scatter(x=timestampnew, y=temperaturanew,
                    mode='lines',
                    text='Temperatura SENSOR 1',
                    line = dict(color='orange', width=4))) 
       figureT.add_trace(go.Scatter(x=timestampnew, y=temperaturanew,
                    mode='markers',
                    text='Temperatura SENSOR 1',
                    line = dict(color='#F96933', width=4)))
       figureT.update_layout(title='Gráfica de Temperatura',
                    xaxis_title='Fecha',
                    yaxis_title='Temperatura °C') 
       figureT.show()
       
       figureH = go.Figure()
       figureH.add_trace(go.Scatter(x=timestampnew, y=humedadnew,
                    mode='lines',
                    text='Humedad SENSOR 1',
                    line = dict(color='#03A4FD', width=4)))
       figureH.add_trace(go.Scatter(x=timestampnew, y=humedadnew,
                    mode='markers',
                    text='Humedad SENSOR 1',
                    line = dict(color='#3764F5', width=4)))
       figureH.update_layout(title='Gráfica de Humedad',
                    xaxis_title='Fecha',
                    yaxis_title='Humedad %')
       figureH.show()
       """
       figure={
            'data': [
                {'x': timestampnew, 'y': temperaturanew, 'mode':'lines', 'name': 'Temperatura sensor 1'},
                {'x': timestampnew, 'y': humedadnew, 'type': 'scatter', 'name': 'Humedad sensor 1'}, 
            ],
            'layout': {
                'title': 'Gráfica de datos de Temperatura y Humedad'
            }
        }
        """
   return figureT, figureH

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=80)
