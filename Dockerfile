FROM detect-abnormal-set-of-temperatures-base:latest

# Definition of a Device & Service
ENV POSITION=Runtime \
    SERVICE=detect-abnormal-set-of-temperatures \
    AION_HOME=/var/lib/aion

WORKDIR ${AION_HOME}
# Setup Directoties
RUN mkdir -p \
    $POSITION/$SERVICE
WORKDIR ${AION_HOME}/$POSITION/$SERVICE/
ADD . .
RUN python3 setup.py install

CMD ["/bin/sh", "docker-entrypoint.sh"]
