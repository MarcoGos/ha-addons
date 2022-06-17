#!/usr/bin/with-contenv bashio

export DEVICE=$(bashio::config 'device')
export MQTT_BROKER=$(bashio::config "mqtt_host")
export MQTT_PORT=$(bashio::config "mqtt_port")
export MQTT_USER=$(bashio::config "mqtt_user")
export MQTT_PASS=$(bashio::config "mqtt_pass")
export USE_METRIC=$(bashio::config "use_metric")
export INTERVAL=$(bashio::config "interval")

python3 -u ./vproweather2mqtt.py
