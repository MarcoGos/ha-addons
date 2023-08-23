#!/usr/bin/with-contenv bashio

bashio::log.level $(bashio::config "log_level")
LOG_LEVEL=$(bashio::config "log_level")
MAX_OFFSET=$(bashio::config "max_offset")
DETAILED=$(bashio::config "detailed")
UNIT_SYSTEM=$(bashio::config "unit_system")

ARGS=" -l ${LOG_LEVEL}"
ARGS+=" -m ${MAX_OFFSET}"
if [ "$DETAILED" = true ]; then
    ARGS+=" -d"
fi
ARGS+=" -s ${UNIT_SYSTEM}"
bashio::log.info "Args: $ARGS"

python3 -u ./grabforecast.py $ARGS
