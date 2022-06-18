#!/usr/bin/with-contenv bashio

if ! bashio::services.available "mqtt"; then
    bashio::log.info "No internal MQTT service found, trying given credentials ..."
    export MQTT_BROKER=$(bashio::config "mqtt_host")
    export MQTT_PORT=$(bashio::config "mqtt_port")
    export MQTT_USER=$(bashio::config "mqtt_user")
    export MQTT_PASS=$(bashio::config "mqtt_pass")
else
    bashio::log.info "MQTT service found, fetching credentials ..."
    export MQTT_BROKER=$(bashio::services mqtt "host")
    export MQTT_PORT=$(bashio::services mqtt "port")
    export MQTT_USER=$(bashio::services mqtt "username")
    export MQTT_PASS=$(bashio::services mqtt "password")
fi

export DEVICE=$(bashio::config 'device')
export INTERVAL=$(bashio::config "interval")
export USE_METRIC=$(bashio::config "use_metric")

python3 -u ./vproweather2mqtt.py
