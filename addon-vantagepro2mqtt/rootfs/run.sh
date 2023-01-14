#!/usr/bin/with-contenv bashio

bashio::log.level $(bashio::config "log_level")

if ! bashio::services.available "mqtt" && ! bashio::config.exists 'mqtt_host'; then
    bashio::log.info "No internal MQTT service found and no MQTT server defined, Please install Mosquitto broker or specify your own."
    exit 2
else
    bashio::log.info "MQTT available, fetching server details ..."
    if ! bashio::config.exists 'mqtt_host'; then
        bashio::log.info "MQTT server settings not configured, trying to auto-discovering ..."
        MQTT_BROKER=$(bashio::services mqtt "host")
        MQTT_PORT=$(bashio::services mqtt "port")
        MQTT_USER=$(bashio::services mqtt "username")
        MQTT_PASS=$(bashio::services mqtt "password")
    else
        bashio::log.info "MQTT credentials configured, using those ..."
        MQTT_BROKER=$(bashio::config "mqtt_host")
        MQTT_PORT=$(bashio::config "mqtt_port" 1833)
        MQTT_USER=$(bashio::config "mqtt_user")
        MQTT_PASS=$(bashio::config "mqtt_pass")
    fi
fi

DEVICE=$(bashio::config "device" "")
ADDRESS=$(bashio::config "address" "")
INTERVAL=$(bashio::config "interval" 5)
NEW_SENSOR_USED=$(bashio::config "new_sensor_used")
UNIT_SYSTEM=$(bashio::config "unit_system")
LOG_LEVEL=$(bashio::config "log_level")
DISCOVERY_PREFIX=$(bashio::config "discovery_prefix" "homeassistant")
ALT_WINDSPEED_UOM=$(bashio::config "alt_windspeed_uom")

ARGS=""
if [ "${DEVICE}" != "" ]; then
    ARGS+=" -d ${DEVICE}"
fi
if [ "${ADDRESS}" != "" ]; then 
    ARGS+=" -a ${ADDRESS}"
fi
ARGS+=" -b ${MQTT_BROKER}"
ARGS+=" -P ${MQTT_PORT}"
ARGS+=" -u ${MQTT_USER}"
ARGS+=" -p ${MQTT_PASS}"
ARGS+=" -I ${DISCOVERY_PREFIX}"
ARGS+=" -s ${UNIT_SYSTEM}"
ARGS+=" -i ${INTERVAL}"
ARGS+=" -l ${LOG_LEVEL}"
if [ "$NEW_SENSOR_USED" = true ]; then
    ARGS+=" -n"
fi
if [ "$ALT_WINDSPEED_UOM" = true ]; then
    ARGS+=" -k"
fi

bashio::log.info "$ARGS"

python3 -u ./vantagepro2mqtt.py $ARGS
