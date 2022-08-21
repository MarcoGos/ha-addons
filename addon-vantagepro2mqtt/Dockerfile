ARG BUILD_FROM
FROM $BUILD_FROM

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
  apk add --no-cache \
    python3 \
    py3-pip \
  && pip3 install pyvantagepro \
  && pip3 install paho-mqtt \
  && pip3 install colorlog

COPY rootfs /

WORKDIR /

# Copy data for add-on
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

LABEL \
  io.hass.version="VERSION" \
  io.hass.type="addon" \
  io.hass.arch="armhf|aarch64|i386|amd64"