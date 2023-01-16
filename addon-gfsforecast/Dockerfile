ARG BUILD_FROM
FROM $BUILD_FROM

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
    apk add gfortran \
        python3 \
        py3-pip \
    && pip3 install requests \
    && pip3 install colorlog

WORKDIR /

# Copy data for add-on
COPY rootfs /
ARG BUILD_ARCH
COPY wgrib2/${BUILD_ARCH}/wgrib2 /
RUN chmod a+x /run.sh
RUN chmod a+x /wgrib2

CMD [ "/run.sh" ]
