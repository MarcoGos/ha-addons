ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
    apk add gfortran \
        python3 \
        py3-pip \
    && pip3 install requests \
    && pip3 install colorlog \
    && pip3 install bottle

WORKDIR /

# Copy data for add-on
COPY rootfs /
ARG BUILD_ARCH
COPY wgrib2/${BUILD_ARCH}/wgrib2 /usr/bin/gfsweatherforecast

RUN chmod a+x /usr/bin/gfsweatherforecast/wgrib2
RUN chmod a+x /etc/services.d/gfsweatherforecast_api/run /etc/services.d/gfsweatherforecast_api/finish 
RUN chmod a+x /etc/services.d/gfsweatherforecast/run /etc/services.d/gfsweatherforecast/finish
