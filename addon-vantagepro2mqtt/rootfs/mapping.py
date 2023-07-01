from utils import *

MAPPING = {
    "Datetime": {
        "topic": "DavisTime",
        "long_name": "Davis Time",
        "device_class": "timestamp",
        "entity_category": "diagnostic",
        "icon": "mdi:clock",
        "correction": convert_to_iso_datetime,
        "enable_by_data": True
    },
    "TempOut": {
        "topic": "OutsideTemp",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Temperature (Outside)",
        "conversion": convert_to_celcius,
        "enable_by_data": True
    },
    "TempIn": {
        "topic": "InsideTemp",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Temperature (Inside)",
        "conversion": convert_to_celcius,
        "enable_by_data": True
    },
    "HeatIndex": {
        "topic": "HeatIndex",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Heat Index",
        "icon": "mdi:sun-thermometer-outline",
        "conversion": convert_to_celcius,
        "enable_by_data": True
    },
    "WindChill": {
        "topic": "WindChill",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Wind Chill",
        "icon": "mdi:snowflake-thermometer",
        "conversion": convert_to_celcius,
        "enable_by_data": True
    },
    "FeelsLike": {
        "topic": "FeelsLike",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Feels Like",
        "conversion": convert_to_celcius,
        "enable_by_data": True
    },
    "DewPoint": {
        "topic": "DewPoint",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Dew Point",
        "icon": "mdi:water-thermometer-outline",
        "conversion": convert_to_celcius,
        "enable_by_data": True
    },
    "Barometer": {
        "topic": "BaroCurr",
        "unit_of_measure": {
            "metric": "hPa",
            "imperial": "inHg"
        }, 
        "device_class": "pressure",
        "state_class": "measurement",
        "long_name": "Barometric Pressure",
        "conversion": convert_to_mbar,
        "enable_by_data": True
    },
    "BarTrend": {
        "topic": "BaroTrend",
        "long_name": "Barometric Trend",
        "correction": get_baro_trend,
        "enable_by_data": True
    },
    "HumIn": {
        "topic": "InsideHum",
        "unit_of_measure": "%",
        "device_class": "humidity",
        "state_class": "measurement",
        "long_name": "Humidity (Inside)",
        "enable_by_data": True
    },
    "HumOut": {
        "topic": "OutsideHum",
        "unit_of_measure": "%",
        "device_class": "humidity", 
        "state_class": "measurement",
        "long_name": "Humidity (Outside)",
        "enable_by_data": True
    },
    "WindSpeed": {
        "topic": "WindSpeed",
        "unit_of_measure": {
            "metric": {
                "default": "km/h",
                "alt": "m/s"
            },
            "imperial": "mph"
        },
        "long_name": "Wind Speed",
        "icon": "mdi:weather-windy",
        "state_class": "measurement",
        "conversion": {
            "default": convert_to_kmh,
            "alt": convert_to_ms
        },
        "enable_by_data": True
    },
    "WindSpeed10Min": {
        "topic": "WindAvgSpeed",
        "unit_of_measure": {
            "metric": {
                "default": "km/h",
                "alt": "m/s"
            },
            "imperial": "mph"
        },
        "long_name": "Wind Speed (Average)",
        "icon": "mdi:weather-windy",
        "state_class": "measurement",
        "conversion": {
            "default": convert_to_kmh,
            "alt": convert_to_ms
        },
        "enable_by_data": True
    },
    "WindDir": {
        "topic": "WindDir",
        "unit_of_measure": "°",
        "long_name": "Wind Direction",
        "icon": "mdi:compass-outline",
        "state_class": "measurement",
        "enable_by_data": True
    },
    "WindDirRose": {
        "topic": "WindDirRose",
        "long_name": "Wind Direction Rose",
        "icon": "mdi:compass-outline",
        "enable_by_data": True
    },
    "WindSpeedBft": {
        "topic": "WindSpeedBft",
        "long_name": "Wind Speed (Bft)",
        "icon": "mdi:weather-windy",
        "state_class": "measurement",
        "enable_by_data": True
    },
    "RainDay": {
        "topic": "DayRain",
        "unit_of_measure": {
            "metric": "mm",
            "imperial": "inch"
        },
        "icon": 'mdi:water',
        "long_name": "Rain (Day)",
        "state_class": "total_increasing",
        "conversion": convert_to_mm,
        "enable_by_data": True
    },
    "RainMonth": {
        "topic": "MonthRain",
        "unit_of_measure": {
            "metric": "mm",
            "imperial": "inch"
        },
        'icon': 'mdi:water',
        "long_name": "Rain (Month)",
        "conversion": convert_to_mm,
        "enable_by_data": True
    },
    "RainYear": {
        "topic": "YearRain",
        "unit_of_measure": {
            "metric": "mm",
            "imperial": "inch"
        },
        'icon': 'mdi:water',
        "long_name": "Rain (Year)",
        "conversion": convert_to_mm,
        "enable_by_data": True
    },
    "RainRate": {
        "topic": "RainRate",
        "unit_of_measure": {
            "metric": "mm/h",
            "imperial": "inch/h"
        },
        "icon": "mdi:water",
        "state_class": "measurement",
        "long_name": "Rain Rate",
        "conversion": convert_to_mm,
        "enable_by_data": True
    },
    "IsRaining": {
        "topic": "IsRaining",
        "long_name": "Is Raining",
        "component": "binary_sensor",
        "enable_by_data": True
    },
    "UV": {
        "topic": "UVLevel",
        "long_name": "UV Level",
        "icon": "mdi:sun-wireless-outline",
        "state_class": "measurement",
        "correction": get_uv,
        "enable_by_data": True
    },
    "SolarRad": {
        "topic": "SolarRad",
        "long_name": "Solar Radiation",
        "icon": "mdi:sun-wireless-outline",
        "state_class": "measurement",
        "correction": get_solar_rad,
        "enable_by_data": True
    },
    "BatteryVolts": {
        "topic": "BattVoltage",
        "unit_of_measure": "V",
        "device_class": "voltage",
        "entity_category": "diagnostic",
        "long_name": "Battery Voltage",
        "correction": round_to_one_decimal,
        "enable_by_data": True
    },
    "ForecastIcon": {
        "topic": "ForeIcon",
        "long_name": "Forecast Icon",
        "enable_by_data": True
    },
    "ForecastRuleNo": {
        "topic": "ForeRule",
        "long_name": "Forecast Rule",
        "icon": "mdi:binoculars",
        "correction": get_forecast_string,
        "enable_by_data": True
    },
    "ExtraTemps01": {
        "topic": "ExtraTemps01",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Extra Temperature 1",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value,
        "enable_by_data": True
    },
    "ExtraTemps02": {
        "topic": "ExtraTemps02",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Extra Temperature 2",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value,
        "enable_by_data": True
    },
    "ExtraTemps03": {
        "topic": "ExtraTemps03",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Extra Temperature 3",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value,
        "enable_by_data": True
    },
    "ExtraTemps04": {
        "topic": "ExtraTemps04",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Extra Temperature 4",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value,
        "enable_by_data": True
    },
    "ExtraTemps05": {
        "topic": "ExtraTemps05",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Extra Temperature 5",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value,
        "enable_by_data": True
    },
    "ExtraTemps06": {
        "topic": "ExtraTemps06",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Extra Temperature 6",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value,
        "enable_by_data": True
    },
    "ExtraTemps07": {
        "topic": "ExtraTemps07",
        "unit_of_measure": {
           "metric": "°C",
           "imperial": "°F"
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "long_name": "Extra Temperature 7",
        "conversion": convert_to_celcius,
        "has_correct_value": has_correct_value,
        "enable_by_data": True
    },
    "Status": {
        "topic": "Status",
        "long_name": "Status",
        "entity_category": "diagnostic",
        "icon": "mdi:check-circle-outline",
        "availability": False
    },
    "LastError": {
        "topic": "LastError",
        "long_name": "Last Error",
        "entity_category": "diagnostic",
        "icon": "mdi:message-alert-outline"
    }
}