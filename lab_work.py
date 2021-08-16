from flask import Flask, request, render_template
import sys
import board
import adafruit_dht
import sqlite3
import time
import datetime
import arrow
import pickle
import os


basedir = os.path.abspath(os.path.dirname(__file__))
weather_pred_model_file = os.path.join(basedir, 'static/ml_models/weather_pred_model.pkl')

with open(weather_pred_model_file, 'rb') as file:
    weather_pred_model = pickle.load(file)

app = Flask(__name__)

@app.route("/weather_hum_temp")
def read_weather_hum_temp():
    dht_device = adafruit_dht.DHT22(board.D17, False)
    humidity = dht_device.humidity
    temperature = dht_device.temperature
    if humidity is not None and temperature is not None:
      rain = predict_rain(humidity, temperature)
      return render_template("current_hum_temp.html",temp=temperature,hum=humidity,rain=rain)
    else:
      return render_template("no_sensor.html")

def predict_rain(hum, temp):
    return "Yes" if weather_pred_model.predict([[hum, temp]])[0] else "No"


@app.route("/weather_temp_hum_vals", methods=["GET"])
def weather_temp_hum_db():
    temp_hum, timezone, from_date_str, to_date_str = get_records()

    print ("QUERY STRING: %s" % request.query_string)

    # Create new record tables so that datetimes are adjusted back to the user browser's time zone.
    time_adjusted_temp_hum = []

    for record in temp_hum:
        local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm:ss").to(timezone)
        time_adjusted_temp_hum.append([local_timedate.format('YYYY-MM-DD HH:mm:ss'), round(record[2],2), round(record[3],2), record[4]])

    return render_template("weather_vals_from_db.html", temp_hum=time_adjusted_temp_hum, temp_hum_items=len(temp_hum), from_date=from_date_str, to_date=to_date_str, query_string=request.query_string)

def get_records():
    from_date_str 	= request.args.get('from',time.strftime("%Y-%m-%d 00:00")) #Get the from date value from the URL
    to_date_str 	= request.args.get('to',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
    timezone            = request.args.get('timezone', 'Etc/UTC')
    range_h_form	= request.args.get('range_h','')  #This will return a string, if field range_h exists in the request

    range_h_int 	= "nan"  #initialise this variable with not a number
    
    try:
        range_h_int	= int(range_h_form)
    except:
        print("range_h_form not a number")

    if not validate_date(from_date_str):			# Validate date before sending it to the DB
        from_date_str 	= time.strftime("%Y-%m-%d 00:00")
    if not validate_date(to_date_str):
        to_date_str 	= time.strftime("%Y-%m-%d %H:%M")		# Validate date before sending it to the DB
    
    # Create datetime object so that we can convert to UTC from the browser's local time
    from_date_obj       = datetime.datetime.strptime(from_date_str,'%Y-%m-%d %H:%M')
    to_date_obj         = datetime.datetime.strptime(to_date_str,'%Y-%m-%d %H:%M')

    # If range_h is defined, we don't need the from and to times
    if isinstance(range_h_int,int):
        arrow_time_from         = arrow.utcnow().shift(hours=-range_h_int)
        arrow_time_to           = arrow.utcnow()
        from_date_utc           = arrow_time_from.strftime("%Y-%m-%d %H:%M")
        to_date_utc             = arrow_time_to.strftime("%Y-%m-%d %H:%M")
        from_date_str           = arrow_time_from.to(timezone).strftime("%Y-%m-%d %H:%M")
        to_date_str	        = arrow_time_to.to(timezone).strftime("%Y-%m-%d %H:%M")
    else:
        #Convert datetimes to UTC so we can retrieve the appropriate records from the database
        from_date_utc   = arrow.get(from_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")
        to_date_utc     = arrow.get(to_date_obj, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")

    conn=sqlite3.connect('/var/www/weather_app/weather_app.db')
    curs=conn.cursor()
    curs.execute("SELECT * FROM weather WHERE rDateTime BETWEEN ? AND ?", (from_date_utc.format('YYYY-MM-DD HH:mm'), to_date_utc.format('YYYY-MM-DD HH:mm')))
    temp_hum = curs.fetchall()
    conn.close()

    return [temp_hum, timezone, from_date_str, to_date_str]

def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
