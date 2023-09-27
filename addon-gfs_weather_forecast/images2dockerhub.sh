docker run \
  --rm \
  --privileged \
  -v ~/.docker:/root/.docker \
  homeassistant/amd64-builder \
  --all \
  -t addon-gfs_weather_forecast \
  -r https://github.com/MarcoGos/ha-addons \
  -b master