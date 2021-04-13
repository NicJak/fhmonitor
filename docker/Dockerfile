FROM python:latest

RUN apt-get update && apt-get install --yes --no-install-recommends inotify-tools

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

WORKDIR /app
COPY fhmonitor/fhmonitor.py .

CMD python /app/fhmonitor.py /config/config.json