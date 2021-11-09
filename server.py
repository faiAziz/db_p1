#!/usr/bin/env python

"""
Columbia's COMS W4111.003 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import math
import pandas as pd

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASEURI = "postgresql://sls2305:6264@35.196.73.133/proj1part2"
#DATABASEURI = "postgresql://fa2602:7831@35.196.73.133/proj1part2"
lat, long = 0, 0 

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.
  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """
  return render_template("index.html")

#borough - find name, date, and violation given borough from dropdown menu
@app.route('/borough', methods=['POST'])
def borough(page=1):
  borough = request.form['borough']
  query = 'SELECT R.name, I.date, V.description FROM restaurant R, address A, violation V, inspection I WHERE R.camis = I.camis AND R.camis = A.camis AND V.iid = I.iid AND A.boro = '
  query = query + '\'' + borough + '\''+ ' LIMIT 500'
  cursor = g.conn.execute(query)
  output = []
  for result in cursor:
    output.append(result)  # can also be accessed using result[0]
  cursor.close()
  df = pd.DataFrame(output, columns= ['Restaurant Name', 'Inspection Date', 'Violation Description'])

  items_per_page = 20
  limit = math.ceil(len(df) / items_per_page)
  start_pos = 0
  if int(page) != 1:
    start_pos = items_per_page * (int(page) - 1)

  data = dict(page=int(page), data=df[start_pos: start_pos + items_per_page].to_html(), limit=limit)

  return render_template('displayitems.html', data=data)

#cuisine - find restaurants and address given cuisine type
@app.route('/cuisine', methods=['POST'])
def cuisine(page=1):
  length = 7
  food = [0] * length
  food[0] = (request.form.get('food1'))
  food[1] = (request.form.get('food2'))
  food[2] = (request.form.get('food3'))
  food[3] = (request.form.get('food4'))
  food[4] = (request.form.get('food5'))
  food[5] = (request.form.get('food6'))
  food[6] = (request.form.get('food7'))

  query = 'SELECT R.name, A.building, A.street, A.zip FROM restaurant R, address A WHERE R.camis = A.camis'
  string_list = ' AND R.cuisine IN ('

  for i in range(length): #go through all foods
    if (food[i] != None): #only add if selected
      string_list = string_list + '\'' + food[i] + '\'' + ',' #append to list

  string_list = string_list[:-1] #remove last comma
  string_list = string_list + ')'

  if (string_list != ' AND R.cuisine IN )'): #check if any values added to string list
    query = query + string_list #run default query if nothing selected

  cursor = g.conn.execute(query)
  output = []
  for result in cursor:
    output.append(result)  # can also be accessed using result[0]
  cursor.close()
  df = pd.DataFrame(output, columns=['Restaurant Name', 'Building', 'Street', 'Zip Code'])

  items_per_page = 20
  limit = math.ceil(len(df) / items_per_page)
  start_pos = 0
  if int(page) != 1:
    start_pos = items_per_page * (int(page) - 1)

  data = dict(page=int(page), data=df[start_pos: start_pos + items_per_page].to_html(), limit=limit)

  return render_template('displayitems.html', data=data)

#latitude - find restaurants above or below a given latitude
@app.route('/latitude', methods=['POST'])
def latitude(page=1):
  latitude = request.form['latitude']
  north_south = request.form['north_south']
  latitude = float(latitude) / 298.93100777 + 40.54298569 #rescale the latitude to size of NYC
  query = 'SELECT R.name, A.latitude FROM restaurant R, address A WHERE R.camis = A.camis AND A.latitude '
  if north_south == 'North':
    query = query + '>='
  elif north_south == 'South':
    query = query + '<='
  query = query + '\'' + str(latitude) + '\''
  cursor = g.conn.execute(query)
  output = []
  for result in cursor:
    output.append(result)  # can also be accessed using result[0]
  cursor.close()
  df = pd.DataFrame(output, columns=['Restaurant Name', 'Latitude'])

  items_per_page = 20
  limit = math.ceil(len(df) / items_per_page)
  start_pos = 0
  if int(page) != 1:
    start_pos = items_per_page * (int(page) - 1)

  data = dict(page=int(page), data=df[start_pos: start_pos + items_per_page].to_html(), limit=limit)

  return render_template('displayitems.html', data=data)

#location - get user location
@app.route('/location', methods=['POST'])
def location():
  global lat
  global long
  lat = request.form.get('js_data[lat]')
  long = request.form.get('js_data[long]')
  return redirect('/')


#radius - find restaurants within a given radius
@app.route('/radius', methods=['POST'])
def radius(page=1):
  global lat
  global long
  radius = int(request.form.get('distance', 1)) * 200 #distance is 0-100 slider, convert to 0-20,000 (in units of meters)
  if (lat != 0 and long != 0):
    query = 'select R.name, R.cuisine from restaurant R, address A where R.camis = A.camis AND ' + str(radius) + '> ( sqrt(((' + str(lat) + ' - A.latitude)* (' + str(
        lat) + ' - A.latitude)) + ((' + str(long) + ' - A.longitude)*(' + str(long) + ' - A.longitude)))* 111139)' #111,139 is conversion from meters to degrees latitude/longitude
    cursor = g.conn.execute(query)
    output = []
    for result in cursor:
      output.append(result)  # can also be accessed using result[0]
    cursor.close()
    df = pd.DataFrame(output, columns=['Restaurant Name', 'Cuisine'])

    items_per_page = 20
    limit = math.ceil(len(df) / items_per_page)
    start_pos = 0
    if int(page) != 1:
      start_pos = items_per_page * (int(page) - 1)

    data = dict(page=int(page), data=df[start_pos: start_pos + items_per_page].to_html(), limit=limit)
  else:
    data = dict(page=1, data='<p>You must allow location first!</p>', limit=1)

  return render_template('displayitems.html', data=data)
  
#grade - print name, date, grade given grade input
@app.route('/grade', methods=['POST'])
def grade(page=1):
  length = 3
  grade = [0] * length
  grade[0] = (request.form.get('grade1'))
  grade[1] = (request.form.get('grade2'))
  grade[2] = (request.form.get('grade3'))

  query = 'SELECT R.name, I.date, G.grade FROM restaurant R, inspection I, grade G WHERE R.camis = I.camis AND I.iid = G.iid'

  string_list = ' AND G.grade IN ('

  for i in range(length): #go through all foods
    if (grade[i] != None): #only add if selected
      string_list = string_list + '\'' + grade[i] + '\'' + ',' #append to list

  string_list = string_list[:-1] #remove last comma
  string_list = string_list + ')'

  if (string_list != ' AND G.grade IN )'): #check if any values added to string list
    query = query + string_list #run default query if nothing selected

  cursor = g.conn.execute(query)
  output = []
  for result in cursor:
    output.append(result)  # can also be accessed using result[0]
  cursor.close()
  df = pd.DataFrame(output, columns=['Restaurant Name', 'Inspection Date', 'Grade'])

  items_per_page = 20
  limit = math.ceil(len(df) / items_per_page)
  start_pos = 0
  if int(page) != 1:
    start_pos = items_per_page * (int(page) - 1)

  data = dict(page=int(page), data=df[start_pos: start_pos + items_per_page].to_html(), limit=limit)

  return render_template('displayitems.html', data=data)

@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:
        python server.py
    Show the help text using:
        python server.py --help
    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded, ssl_context='adhoc')


  run()
