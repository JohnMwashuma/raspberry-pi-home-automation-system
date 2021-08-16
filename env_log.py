import sqlite3
import sys
import adafruit_dht
import board
import pickle
import os
import RPi.GPIO as GPIO
import time

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
rain = "No"
if humidity is not None and temperature is not None:
    rain = predict_rain(humidity, temperature)
    log_values("1", temperature, humidity, rain)
else:
    log_values("1", -999, -999, "No")

def spin_motor():
    GPIO.setwarnings(False)
    servo_pin = 27
    mode = GPIO.getmode()
    # check if the GPIO mode has not been set to GPIO.BCM
    if (mode != 11):
        GPIO.setmode(GPIO.BOARD)
        servo_pin = 13

    GPIO.setup(servo_pin, GPIO.OUT)
    pwd = GPIO.PWM(servo_pin, 50)
    pwd.start(0)
    duty = 2
    while (duty <= 12):
        for i in range(0, 180):
            DC = 1./18.*(i) + duty
            pwd.ChangeDutyCycle(DC)
            time.sleep(0.02)
        for i in range(180, 0, -1):
            DC = 1./18.*(i) + duty
            pwd.ChangeDutyCycle(DC)
            time.sleep(0.02)
        duty = duty + 1
    pwd.stop()
    GPIO.cleanup()

if rain == "No":
    # Spin motor
    spin_motor()
