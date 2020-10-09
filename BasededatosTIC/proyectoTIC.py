from flask import Flask, request
import sqlite3


db_path = 'agriculturadeprecision.db'

app = Flask(__name__)

@app.route('/')
def inicio():
   return "hola mundo",200

@app.route('/resetdb')
def resetdb():
  con = sqlite3.connect(db_path)
  cur = con.cursor()
  cur.execute("DROP TABLE IF EXISTS registro")
  cur.execute("CREATE TABLE registro (idsensor NUMERIC, fecha DATETIME, temperatura NUMERIC, humedadambiente NUMERIC, humedadsuelo NUMERIC, latitud NUMERIC, longitud NUMERIC, altitud NUMERIC, lux NUMERIC)")
  con.commit()
  con.close()
  return "borrado",201

@app.route('/datos',methods=['POST'])
def recibirdatos():
  valores = request.values
  print(str(valores))
  a = str(request.values.get('id'))
  d1 = a.split(';')[0]
  d2 = a.split(';')[1].split('=')[1]
  d3 = a.split(';')[2].split('=')[1]
  d4 = a.split(';')[3].split('=')[1]
  d5 = a.split(';')[4].split('=')[1]
  d6 = a.split(';')[5].split('=')[1]
  d7 = a.split(';')[6].split('=')[1]
  d8 = a.split(';')[6].split('=')[1]
  con = sqlite3.connect(db_path)
  cur = con.cursor()
  cur.execute("INSERT INTO registro VALUES("+d1 +"," + "datetime('now')" +"," +d2 +","+d3 +","+d4 +","+d5 +","+d6 +","+d7 +","+d8 +")")
  con.commit()
  con.close()
  return "OK",201


if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=80)
