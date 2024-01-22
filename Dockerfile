FROM python:latest

RUN pip3 install pyyaml screepsapi prometheus_client
COPY screeps_exporter /opt/screeps_exporter
COPY start_exporter.py /opt/start_exporter.py
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]