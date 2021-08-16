import sqlite3
import sys
import adafruit_dht
import board
import pickle
import os

basedir = os.path.abspath(os.path.dirname(__file__))
weather_pred_model_file = os.path.join(basedir, 'static/ml_models/weather_pred_model.pkl')
with open(weather_pred_model_file, 'rb') as file:
    weather_pred_model = pickle.load(file)

def log_values(sensor_id, temp, hum, rain):
    conn = sqlite3.connect('/var/www/weather_app/weather_app.db')
    curs = conn.cursor()
    curs.execute("""INSERT INTO weather values(datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?), (?), (?))""", (sensor_id, temp, hum, rain))
    conn.commit()
    conn.close()

def predict_rain(hum, temp):
    return "Yes" if weather_pred_model.predict([[hum, temp]])[0] else "No"

dht_device = adafruit_dht.DHT22(board.D17)
humidity = dht_device.humidity
temperature = dht_device.temperature
if humidity is not None and temperature is not None:
    rain = predict_rain(humidity, temperature)
    log_values("1", temperature, humidity, rain)
else:
    log_values("1", -999, -999, "No")

