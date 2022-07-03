from utils import *

MAPPING = {
    "Datetime": {
        "topic": "DavisTime",
        "long_name": "Davis Time",
        "correction_function": convert_to_iso_datetime
    },
    "TempOut": {
        "topic": "OutsideTemp",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Temperature",
        "conversion": convert_to_celcius
    },
    "TempIn": {
        "topic": "InsideTemp",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Temperature (Inside)",
        "conversion": convert_to_celcius
    },
    "HeatIndex": {
        "topic": "HeatIndex",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Heat Index",
        "conversion": convert_to_celcius
    },
    "WindChill": {
        "topic": "WindChill",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Wind Chill",
        "conversion": convert_to_celcius
    },
    "FeelsLike": {
        "topic": "FeelsLike",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Feels Like",
        "conversion": convert_to_celcius
    },
    "Barometer": {
        "topic": "BaroCurr",
        "unit_of_measure": {
            "metric": "hPa",
            "imperial": "inHg"
        }, 
        "device_class": "pressure",
        "long_name": "Barometric Pressure",
        "conversion": convert_to_mbar
    },
    "BarTrend": {
        "topic": "BaroTrend",
        "long_name": "Barometric Trend"
    },
    "HumIn": {
        "topic": "InsideHum",
        "unit_of_measure": "%",
        "long_name": "Humidity (Inside)"
    },
    "HumOut": {
        "topic": "OutsideHum",
        "unit_of_measure": "%",
        "long_name": "Humidity (Outside)"
    },
    "WindSpeed": {
        "topic": "WindSpeed",
        "unit_of_measure": {
            "metric": "km/h",
            "imperial": "mph"
        },
        "long_name": "Wind Speed",
        "icon": "mdi:weather-windy",
        "conversion": convert_to_kmh
    },
    "WindSpeed10Min": {
        "topic": "WindAvgSpeed",
        "unit_of_measure": {
            "metric": "km/h",
            "imperial": "mph"
        },
        "long_name": "Wind 10 minute Average Speed",
        "icon": "mdi:weather-windy",
        "conversion": convert_to_kmh
    },
    "WindDir": {
        "topic": "WindDir",
        "unit_of_measure": "°",
        "long_name": "Wind Direction"
    },
    "WindDirRose": {
        "topic": "WindDirRose",
        "long_name": "Wind Direction Rose"
    },
    "WindSpeedBft": {
        "topic": "WindSpeedBft",
        "long_name": "Wind Speed (Bft)"
    },
    "RainDay": {
        "topic": "DayRain",
        "unit_of_measure": {
            "metric": "mm",
            "imperial": "inch"
        },
        "icon": 'mdi:water',
        "long_name": "Rain (Day)",
        "conversion": convert_to_mm
    },
    "RainMonth": {
        "topic": "MonthRain",
        "unit_of_measure": {
            "metric": "mm",
            "imperial": "inch"
        },
        'icon': 'mdi:water',
        "long_name": "Rain (Month)",
        "conversion": convert_to_mm
    },
    "RainYear": {
        "topic": "YearRain",
        "unit_of_measure": {
            "metric": "mm",
            "imperial": "inch"
        },
        'icon': 'mdi:water',
        "long_name": "Rain (Year)",
        "conversion": convert_to_mm
    },
    "RainRate": {
        "topic": "RainRate",
        "unit_of_measure": {
            "metric": "mm/h",
            "imperial": "inch/h"
        },
        "icon": "mdi:water",
        "long_name": "Rain Rate",
        "conversion": convert_to_mm
    },
    "UV": {
        "topic": "UVLevel",
        "long_name": "UV Level"
    },
    "SolarRad": {
        "topic": "SolarRad",
        "long_name": "Solar Radiation"
    },
    "BatteryVolts": {
        "topic": "BattVoltage",
        "unit_of_measure": "V",
        "device_class": "voltage",
        "long_name": "Battery Voltage"
    },
    "ForecastIcon": {
        "topic": "ForeIcon",
        "long_name": "Forecast Icon"
    },
    "ForecastRuleNo": {
        "topic": "ForeRule",
        "long_name": "Forecast Rule"
    },
    "ExtraTemps01": {
        "topic": "ExtraTemps01",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Extra Temperature 1",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value
    },
    "ExtraTemps02": {
        "topic": "ExtraTemps02",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Extra Temperature 2",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value
    },
    "ExtraTemps03": {
        "topic": "ExtraTemps03",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Extra Temperature 3",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value
    },
    "ExtraTemps04": {
        "topic": "ExtraTemps04",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Extra Temperature 4",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value
    },
    "ExtraTemps05": {
        "topic": "ExtraTemps05",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Extra Temperature 5",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value
    },
    "ExtraTemps06": {
        "topic": "ExtraTemps06",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Extra Temperature 6",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value
    },
    "ExtraTemps07": {
        "topic": "ExtraTemps07",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "long_name": "Extra Temperature 7",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value
    },
}