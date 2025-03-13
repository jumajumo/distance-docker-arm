FROM python:3.11-slim

# Install system dependencies and RPi.GPIO
RUN apt-get update && apt-get install -y \
    python3-rpi.gpio \
    cron \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip install --no-cache-dir paho-mqtt RPi.GPIO


ADD cron /var/jumajumo/cron
RUN crontab /var/jumajumo/cron

ADD publish.py /var/jumajumo/publish.py
RUN chmod +x /var/jumajumo/publish.py

CMD ["python3", "/var/jumajumo/publish.py"]

