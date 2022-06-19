import json
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
interval = int(os.environ['INTERVAL']) if 'INTERVAL' in os.environ else 5

long_names = {
    "15mRain": "15 Minute Rain",
    "BaroCurr": "Pressure",
    "BaroTrend": "Barometer Trend",
    "BaroTrendImg": "Barometer Trend Image",
    "BattVoltage": "Battery Voltage",
    "DavisTime": "Davis Time",
    "DayET": "Day ET",
    "DayRain": "Day Rain",
    "ExtraTemp1": "Extra Temperature 1",
    "ExtraTemp2": "Extra Temperature 2",
    "ExtraTemp3": "Extra Temperature 3",
    "ExtraTemp4": "Extra Temperature 4",
    "ExtraTemp5": "Extra Temperature 5",
    "ExtraTemp6": "Extra Temperature 6",
    "ExtraTemp7": "Extra Temperature 7",
    "ForeIcon": "Forecast Icon",
    "ForeRule": "Forecast Rule",
    "Forecast": "Forecast",
    "HeatIndex": "Heat Index",
    "HourRain": "Hour Rain",
    "InsideHum": "Inside Humidify",
    "InsideTemp": "Inside Temperature",
    "IsRaining": "Is Raining",
    "LeafTemp1": "Leaf Temperature 1",
    "LeafTemp2": "Leaf Temperature 2",
    "LeafTemp3": "Leaf Temperature 3",
    "LeafTemp4": "Leaf Temperature 4",
    "MonthET": "Month ET",
    "MonthRain": "Month Rain",
    "NextArchiveRecord": "Next Archive Record",
    "OutsideHum": "Outside Humidity",
    "OutsideTemp": "Outside Temperature",
    "RainRate": "Rain Rate",
    "RainStorm": "Rain Storm",
    "SoilTemp1": "Soil Temperature 1",
    "SoilTemp2": "Soil Temperature 2",
    "SoilTemp3": "Soil Temperature 3",
    "SoilTemp4": "Soil Temperature 4",
    "SolarRad": "Solar Radiation",
    "StormStartDate": "Storm Start Date",
    "ThswIndex": "THSW Index",
    "UVLevel": "UV Level",
    "Wind10mGustMaxDir": "Wind 10 minute Gust Max. Direction",
    "Wind10mGustMaxDirRose": "Wind 10 minute Gust Max. Direction Rose",
    "Wind10mGustMaxSpeed": "Wind 10 minute Gust Max. Speed",
    "Wind2mAvgSpeed": "Wind 2 minute Average Speed",
    "WindAvgSpeed": "Wind Average Speed",
    "WindChill": "Wind Chill",
    "WindDir": "Wind Direction",
    "WindDirRose": "Wind Direction Rose",
    "WindSpeed": "Wind Speed",
    "WindSpeedBft": "Wind Speed Bft",
    "XmitBattt": "Transmit Battery",
    "YearRain": "Year Rain"
}

json_data = {}
static_topic = 'homeassistant'
prefix = 'vproweather'
hass_configured = False

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

def convert_kmh_to_bft(windspeed_kmh):
    return convert_ms_to_bft(convert_kmh_to_ms(windspeed_kmh))

def check_if_correct_data(json_data):
    return json_data['OutsideTemp']['value'] < 60 \
        and json_data['RainRate']['value'] < 1000 \
        and json_data['WindSpeed']['value'] < 40 \
        and json_data['OutsideHum']['value'] < 100

def get_long_name(name):
    if name in long_names:
        return long_names[name]
    else:
        return name

def calc_heat_index(temperature_f, humidity):
    if temperature_f < 80.0 or humidity < 40.0:
        return convert_to_celcius(temperature_f)
    else:
        heat_index = \
            -42.379 \
            + (2.04901523 * temperature_f) \
            + (10.14333127 * humidity) \
            - (0.22475541 * temperature_f * humidity) \
            - (0.00683783 * pow(temperature_f, 2)) \
            - (0.05481717 * pow(humidity, 2)) \
            + (0.00122874 * pow(temperature_f, 2) * humidity) \
            + (0.00085282 * temperature_f * pow(humidity, 2)) \
            - (0.00000199 * pow(temperature_f, 2) * pow(humidity, 2))

    if (heat_index < temperature_f):
        heat_index = temperature_f

    if use_metric:
        return convert_to_celcius(heat_index)
    else:
        return heat_index

def convert_raw_data_to_json(raw_data):
    data_lines = raw_data.split('\n')
    json_data = {}
    for line in data_lines:
        try:
            key,value = line.split(' = ', 1)
            key = key.lstrip('rt')
            value = value.strip()
            try:
                fvalue = float(value)
                if (key in ['InsideTemp', 'OutsideTemp', 'HeatIndex', 'WindChill'] 
                    or key.startswith('ExtraTemp')
                    or key.startswith('SoilTemp')
                    or key.startswith('LeafTemp')):
                    json_data[key] = { 
                        'value': convert_to_celcius(fvalue),
                        'value_F': fvalue,
                        'unit_of_measure': '°C' if use_metric else '°F', 
                        'device_class': 'temperature' }
                elif (key in ['BaroCurr']):
                    json_data[key] = { 
                        'value': convert_to_mbar(fvalue), 
                        'unit_of_measure': 'hPa' if use_metric else "inHg", 
                        'device_class': 'pressure' }
                elif (key in ['RainStorm', 'DayRain', 'MonthRain', 'YearRain', 'DayET', 'MonthET', '15mRain', 'HourRain']):
                    json_data[key] = { 
                        'value': convert_to_mm(fvalue), 
                        'unit_of_measure': 'mm' if use_metric else "inch",
                        'icon': 'mdi:water' }
                elif (key in ['RainRate']):
                    json_data[key] = { 
                        'value': convert_to_mm(fvalue), 
                        'unit_of_measure': 'mm/h' if use_metric else "inch/h",
                        'icon': 'mdi:water' }
                elif (key in ['WindSpeed', 'WindAvgSpeed', 'Wind2mAvgSpeed', 'Wind10mGustMaxSpeed']):
                    json_data[key] = {
                        'value': convert_to_kmh(fvalue), 
                        'unit_of_measure': 'km/h' if use_metric else "mph",
                        'icon': 'mdi:weather-windy' }
                elif (key in ['InsideHum', 'OutsideHum'] or key.startswith('ExtraHum')):
                    json_data[key] = { 
                        'value': fvalue, 
                        'unit_of_measure': '%', 
                        'device_class': 'humidity' }
                elif (key in ['BattVoltage']):
                    json_data[key] = { 
                        'value': fvalue, 
                        'unit_of_measure': 'V',
                        'device_class': 'voltage'}
                elif (key in ['SolarRad']):
                    json_data[key] = {
                        'value': fvalue,
                        'unit_of_measure': 'W/m2'
                    }
                else:
                    json_data[key] = { 'value': fvalue }

            except:
                if (key in ['IsRaining']):
                    json_data[key] = {
                        'value': 'ON' if value == 'yes' else 'OFF',
                        'component': 'binary_sensor'
                    }
                elif (key in ['SolarRad']):
                    json_data[key] = {
                        'value': value,
                        'unit_of_measure': 'W/m2'
                    }
                else:
                    json_data[key] = { 'value': value }
        except ValueError as e:
            pass

    # Overwrite HeatIndex read from Davis
    if 'OutsideTemp' in json_data and 'OutsideHum' in json_data and not 'HeatIndex' in json_data:
        json_data['HeatIndex'] = { 
            'value': calc_heat_index(json_data['OutsideTemp']['value_F'], json_data['OutsideHum']['value']),
            'unit_of_measure': '°C' if use_metric else '°F', 
            'device_class': 'temperature'
        }

    if use_metric and 'WindAvgSpeed' in json_data:
        json_data['WindSpeedBft'] = { 'value': convert_kmh_to_bft(json_data['WindAvgSpeed']['value']), 'unit_of_measure': 'Bft' }
    return json_data

def send_config_to_mqtt(client, json_data):
    for key, raw_value in json_data.items():
        device_class = '' 
        unit_of_measure = ''
        component = 'sensor'
        icon = ''
        if 'unit_of_measure' in raw_value:
            unit_of_measure = raw_value['unit_of_measure']
        if 'device_class' in raw_value:
            device_class = raw_value['device_class']
        if 'icon' in raw_value:
            icon = raw_value['icon']
        if 'component' in raw_value:
            component = raw_value['component']
        config_payload = {}
        config_payload["~"] = static_topic + '/' + component + '/' + prefix + '/' + key
        config_payload["name"] = prefix + " " + get_long_name(key) 
        config_payload["stat_t"] = "~/state"
        config_payload["uniq_id"] = "sensor." + prefix + "_" + key.lower()
        config_payload['dev'] = { "ids": [prefix], "name": prefix, "mf": "Davis", "mdl": "Vantage Pro 2"  }
        if unit_of_measure:
            config_payload["unit_of_meas"] = unit_of_measure
        if device_class:
            config_payload["dev_cla"] = device_class
        if icon:
            config_payload['ic'] = icon
        client.publish(config_payload["~"] + '/config', json.dumps(config_payload), retain=True)

def send_data_to_mqtt(client, json_data):
    for key, raw_value in json_data.items():
        component = 'sensor'
        value = raw_value['value']
        if 'component' in raw_value:
            component = raw_value['component']
        client.publish(static_topic + '/' + component + '/' + prefix + '/' + key + '/state', value, retain=True)

#
# MAIN
#
client = mqtt.Client()

if mqtt_user and mqtt_pass:
    client.username_pw_set(mqtt_user, mqtt_pass)

try:
    client.connect(broker, port)
except:
    logging.error("Connection to MQTT failed. Make sure broker, port, and user is defined correctly")
    exit(1)

while True:
    ready_to_send = True
    logging.info('Acquiring data from ' + device + ' using vproweather')
    process = '/vproweather/vproweather -x -t -d 15 ' + device + ' 2>/dev/null'
    logging.debug('Executing ' + process)
    output = os.popen(process)
    data = output.read()
    output.close()
    if data == '':
        logging.error('Error acquiring data')
        client.disconnect()
        exit(2)

    json_data = convert_raw_data_to_json(data)

    if not check_if_correct_data(json_data):
        logging.error('Incorrect data found:' + json.dumps(json_data))
        ready_to_send = False

    if ready_to_send:
        if not hass_configured:
            logging.info('Initializing sensors from Home Assistant to auto discover.')
            send_config_to_mqtt(client, json_data)
            hass_configured = True

        send_data_to_mqtt(client, json_data)
        logging.info('Data sent to MQTT')

    time.sleep(interval)
