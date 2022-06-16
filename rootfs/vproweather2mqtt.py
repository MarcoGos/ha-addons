from curses import raw
import json
import getopt
import sys
import os
import paho.mqtt.client as mqtt 

try:
     broker = os.environ['MQTTBROKER']
except:
    print("Must define MQTT Broker in configuration!")
    exit(1)

port = int(os.environ['MQTTPORT']) if 'MQTTPORT' in os.environ else 1883
mqttuser = os.environ['MQTTUSER'] if 'MQTTUSER' in os.environ else ""
mqttpass = os.environ['MQTTPASS'] if 'MQTTPASS' in os.environ else ""
hass_configured = os.environ['HASS_CONFIGURED'] if 'HASS_CONFIGURED' in os.environ else "" # "done" or ""

json_data = {}

metric = True
static_topic = 'homeassistant'
base_topic =  static_topic + '/sensor/vproweather'

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:', ['data='])
except getopt.GetoptError:
    print('vproweather2mqtt.py -d <data>')
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-d', '--data'):
        data = arg

data_lines = data.split('\n')
def convert_to_celcius(value):
    return round((value - 32.0) * (5.0/9.0), 1) if metric else value
    
def convert_to_kmh(value):
    return round(value * 1.609344, 1) if metric else value

def convert_to_mbar(value):
    return round(value * 33.8637526, 1) if metric else value

def convert_to_mm(value):
    return round(value * 25.4, 1) if metric else value

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

for line in data_lines:
    try:
        key,value = line.split(' = ', 1)
        key = key.lstrip('rt')
        value = value.strip()
        try:
            fvalue = float(value)
            if (key in ['InsideTemp', 'OutsideTemp', 'HeatIndex', 'WindChill']):
                json_data[key] = { 'value': convert_to_celcius(fvalue), 'unit_of_measure': '°C' if metric else '°F', 'device_class': 'temperature' }
            elif (key in ['BaroCurr']):
                json_data[key] = { 'value': convert_to_mbar(fvalue), 'unit_of_measure': 'hPa' if metric else "inHg", 'device_class': 'pressure' }
            elif (key in ['RainStorm', 'DayRain', 'MonthRain', 'YearRain', 'DayET', 'MonthET', '15mRain', 'HourRain']):
                json_data[key] = { 'value': convert_to_mm(fvalue), 'unit_of_measure': 'mm' if metric else "inch" }
            elif (key in ['RainRate']):
                json_data[key] = { 'value': convert_to_mm(fvalue), 'unit_of_measure': 'mm/h' if metric else "inch/h" }
            elif (key in ['WindSpeed', 'WindAvgSpeed', 'Wind2mAvgSpeed', 'Wind10mGustMaxSpeed']):
                json_data[key] = { 'value': convert_to_kmh(fvalue), 'unit_of_measure': 'km/h' if metric else "mph" }
            elif (key in ['InsideHum', 'OutsideHum']):
                json_data[key] = { 'value': value, 'unit_of_measure': '%', 'device_class': 'humidity' }
            elif (key in ['rtBattVoltage']):
                json_data[key] = { 'value': fvalue, 'unit_of_measure': 'V', 'device_class': 'voltage'}
            else:
                json_data[key] = fvalue
        except:
            json_data[key] = value
    except ValueError as e:
        pass

if metric:
    json_data['WindSpeedBft'] = { 'value': convert_ms_to_bft(convert_kmh_to_ms(float(json_data['WindAvgSpeed']['value']))), 'unit_of_measure': 'Bft' }

print("Establishing MQTT to "+broker+" port "+str(port)+"...")
client = mqtt.Client()

if mqttuser and mqttpass:
    print("(Using MQTT username " + mqttuser + ")")
    client.username_pw_set(mqttuser, mqttpass)

try:
    client.connect(broker, port)
except:
    print("Connection failed. Make sure broker, port, and user is defined correctly")
    exit(1)

if hass_configured != 'done':
    print('Sending config payload to home assistant')
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

os.environ["HASS_CONFIGURED"] = 'done'

client.disconnect()
print('published to mqtt')
