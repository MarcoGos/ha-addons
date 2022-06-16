ARG BUILD_FROM=hassioaddons/base:8.0.6
FROM $BUILD_FROM

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

#ARG BUILD_ARCH
RUN \
  apk add --no-cache \
    git \
    build-base \
    make \
    python3 \
    py3-pip \
  && pip3 install paho-mqtt \
  && git clone https://github.com/bytesnz/vproweather.git \
  && cd vproweather \
  && make all

COPY rootfs /

WORKDIR \
  /

# Copy data for add-on
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
