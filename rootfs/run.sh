#!/usr/bin/with-contenv bashio

export DEVICE=$(bashio::config 'device')
export MQTTBROKER=$(bashio::config "mqtt_host")
export MQTTPORT=$(bashio::config "mqtt_port")
export MQTTUSER=$(bashio::config "mqtt_user")
export MQTTPASS=$(bashio::config "mqtt_pass")

while true
do
  {
    DATA=`/vproweather/vproweather -x -t -d 15 $DEVICE`
  } || {
    echo "Gotten an error"
  }
  echo `python3 -u ./vproweather2mqtt.py -d "$DATA"`
  sleep 5
done
