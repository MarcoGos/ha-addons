#!/usr/bin/with-contenv bashio

bashio::log.level $(bashio::config "log_level")

if ! bashio::services.available "mqtt" && ! bashio::config.exists 'mqtt_host'; then
    bashio::log.info "No internal MQTT service found and no MQTT server defined, Please install Mosquitto broker or specify your own."
    exit 2
else
    bashio::log.info "MQTT available, fetching server details ..."
    if ! bashio::config.exists 'mqtt_host'; then
        bashio::log.info "MQTT server settings not configured, trying to auto-discovering ..."
        export MQTT_BROKER=$(bashio::services mqtt "host")
        export MQTT_PORT=$(bashio::services mqtt "port")
        export MQTT_USER=$(bashio::services mqtt "username")
        export MQTT_PASS=$(bashio::services mqtt "password")
    else
        bashio::log.info "MQTT credentials configured, using those ..."
        export MQTT_BROKER=$(bashio::config "mqtt_host")
        export MQTT_PORT=$(bashio::config "mqtt_port")
        export MQTT_USER=$(bashio::config "mqtt_user")
        export MQTT_PASS=$(bashio::config "mqtt_pass")
    fi
fi

export DEVICE=$(bashio::config 'device')
export INTERVAL=$(bashio::config "interval")
export NEW_SENSOR_USED=$(bashio::config "new_sensor_used")
export USE_SYSTEM=$(bashio::config "use_system")
export LOG_LEVEL=$(bashio::config "log_level")

python3 -u ./vproweather2mqtt.py
