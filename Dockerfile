FROM python:3.13
RUN mkdir /app
WORKDIR /app
RUN python3 -m venv venv
RUN /app/venv/bin/pip3 install git+https://github.com/martydingo/screeps-exporter
ENTRYPOINT [ "/app/venv/bin/python3", "-m", "screeps_exporter", "-c", "/app/config.yml" ]

