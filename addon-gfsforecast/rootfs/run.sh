#!/usr/bin/with-contenv bashio

bashio::log.level $(bashio::config "log_level")
LOG_LEVEL=$(bashio::config "log_level")
MAX_OFFSET=$(bashio::config "max_offset")

ARGS=" -l ${LOG_LEVEL}"
ARGS+=" -m ${MAX_OFFSET}"
bashio::log.info "Args: $ARGS"

python3 -u ./grabforecast.py $ARGS
