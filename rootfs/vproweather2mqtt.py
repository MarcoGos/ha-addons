from curses import raw
import json
import getopt
import sys
import os
import paho.mqtt.client as mqtt 
import logging
import time

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S') 

try:
    broker = os.environ['MQTT_BROKER']
except:
    logging.error("Must define MQTT Broker in configuration!")
    exit(1)

try:
    device = os.environ['DEVICE']
except:
    logging.error("Must define DEVICE in configuration!")
    exit(1)

port = int(os.environ['MQTT_PORT']) if 'MQTT_PORT' in os.environ else 1883
mqtt_user = os.environ['MQTT_USER'] if 'MQTT_USER' in os.environ else ""
mqtt_pass = os.environ['MQTT_PASS'] if 'MQTT_PASS' in os.environ else ""
use_metric = bool(os.environ['USE_METRIC']) if 'USE_METRIC' in os.environ else True
hass_configured = os.environ['HASS_CONFIGURED'] if 'HASS_CONFIGURED' in os.environ else "" # "done"

json_data = {}
static_topic = 'homeassistant'
base_topic =  static_topic + '/sensor/vproweather'

def convert_to_celcius(value):
    return round((value - 32.0) * (5.0/9.0), 1) if use_metric else value
    
def convert_to_kmh(value):
    return round(value * 1.609344, 1) if use_metric else value

def convert_to_mbar(value):
    return round(value * 33.8637526, 1) if use_metric else value

def convert_to_mm(value):
    return round(value * 25.4, 1) if use_metric else value

def convert_kmh_to_ms(windspeed):
    return round(windspeed / 3.6, 1)

def convert_ms_to_bft(windspeed):
    if windspeed < 0.2:
        return 0
    elif windspeed < 1.6:
        return 1
    elif windspeed < 3.4:
        return 2
    elif windspeed < 5.5:
        return 3
    elif windspeed < 8.0:
        return 4
    elif windspeed < 10.8:
        return 5
    elif windspeed < 13.9: 
        return 6
    elif windspeed < 17.2:
        return 7
    elif windspeed < 20.8:
        return 8
    elif windspeed < 24.5:
        return 9
    elif windspeed < 28.5:
        return 10
    elif windspeed < 32.7:
        return 11
    else:
        return 12

def check_if_correct_data():
    return json_data['OutsideTemp']['value'] < 60 \
        and json_data['RainRate']['value'] < 1000 \
        and json_data['WindSpeed']['value'] < 40 \
        and json_data['OutsideHum']['value'] < 100

#
# MAIN
#
while True:
    logging.info('Acquiring data from ' + device + ' using vproweather')
    logging.debug('Executing /vproweather/vproweather -x -t -d 15 ' + device + ' 2>/dev/null')
    output = os.popen('/vproweather/vproweather -x -t -d 15 ' + device + ' 2>/dev/null')
    data = output.read()
    if output.close() == 'None':
        logging.error('Error acquiring data')
        exit(2)

    data_lines = data.split('\n')

    for line in data_lines:
        try:
            key,value = line.split(' = ', 1)
            key = key.lstrip('rt')
            value = value.strip()
            try:
                fvalue = float(value)
                if (key in ['InsideTemp', 'OutsideTemp', 'HeatIndex', 'WindChill']):
                    json_data[key] = { 'value': convert_to_celcius(fvalue), 'unit_of_measure': '°C' if use_metric else '°F', 'device_class': 'temperature' }
                elif (key in ['BaroCurr']):
                    json_data[key] = { 'value': convert_to_mbar(fvalue), 'unit_of_measure': 'hPa' if use_metric else "inHg", 'device_class': 'pressure' }
                elif (key in ['RainStorm', 'DayRain', 'MonthRain', 'YearRain', 'DayET', 'MonthET', '15mRain', 'HourRain']):
                    json_data[key] = { 'value': convert_to_mm(fvalue), 'unit_of_measure': 'mm' if use_metric else "inch" }
                elif (key in ['RainRate']):
                    json_data[key] = { 'value': convert_to_mm(fvalue), 'unit_of_measure': 'mm/h' if use_metric else "inch/h" }
                elif (key in ['WindSpeed', 'WindAvgSpeed', 'Wind2mAvgSpeed', 'Wind10mGustMaxSpeed']):
                    json_data[key] = { 'value': convert_to_kmh(fvalue), 'unit_of_measure': 'km/h' if use_metric else "mph" }
                elif (key in ['InsideHum', 'OutsideHum']):
                    json_data[key] = { 'value': fvalue, 'unit_of_measure': '%', 'device_class': 'humidity' }
                elif (key in ['rtBattVoltage']):
                    json_data[key] = { 'value': fvalue, 'unit_of_measure': 'V', 'device_class': 'voltage'}
                else:
                    json_data[key] = fvalue
            except:
                json_data[key] = value
        except ValueError as e:
            pass

    if use_metric and 'WindAvgSpeed' in json_data:
        json_data['WindSpeedBft'] = { 'value': convert_ms_to_bft(convert_kmh_to_ms(float(json_data['WindAvgSpeed']['value']))), 'unit_of_measure': 'Bft' }

    if not check_if_correct_data():
        logging.error('Incorrect data found:' + json.dumps(json_data))
        exit(2)

    #logging.info("Establishing MQTT to "+broker+" port "+str(port)+"...")
    client = mqtt.Client()

    if mqtt_user and mqtt_pass:
    #    print("(Using MQTT username " + mqtt_user + ")")
        client.username_pw_set(mqtt_user, mqtt_pass)

    try:
        client.connect(broker, port)
    except:
        logging.error("Connection failed. Make sure broker, port, and user is defined correctly")
        exit(1)

    if hass_configured != 'done':
        logging.info('Initializing sensors from Home Assistant to auto discover.')
        for key, raw_value in json_data.items():
            device_class = '' 
            unit_of_measure = ''
            value = raw_value
            if type(raw_value) is dict:
                value = raw_value['value']
                unit_of_measure = raw_value['unit_of_measure']
                if 'device_class' in raw_value:
                    device_class = raw_value['device_class']
            config_payload = {}
            config_payload["~"] = base_topic + '/' + key
            config_payload["name"] = "vproweather " + key 
            config_payload["stat_t"] = "~/state"
            config_payload["uniq_id"] = "sensor.vproweather_" + key 
            if unit_of_measure:
                config_payload["unit_of_meas"] = unit_of_measure
            if device_class:
                config_payload["dev_cla"] = device_class
            client.publish(config_payload["~"] + '/config', json.dumps(config_payload), retain=True)

    for key, raw_value in json_data.items():
        value = raw_value
        if type(raw_value) is dict:
            value = raw_value['value']
        client.publish(base_topic + '/' + key + '/state', value, retain=True)
    logging.info('Data sent to MQTT')
    client.disconnect()
    #print('published to mqtt')

    time.sleep(5)
