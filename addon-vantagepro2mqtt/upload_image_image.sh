docker run \
  --rm \
  --privileged \
  -v ~/.docker:/root/.docker \
  homeassistant/amd64-builder \
  --all \
  -t addon-vantagepro2mqtt \
  -r https://github.com/MarcoGos/ha-addons \
  -b beta