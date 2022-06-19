ARG BUILD_FROM
FROM $BUILD_FROM

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
  apk add --no-cache \
    git \
    build-base \
    make \
    python3 \
    py3-pip \
  && pip3 install paho-mqtt \
  && git clone https://github.com/MarcoGos/vproweather.git \
  && cd vproweather \
  && make all

COPY rootfs /

WORKDIR /

# Copy data for add-on
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
