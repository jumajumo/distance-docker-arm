FROM hickey/rpi-python3

RUN apt-get update && apt-get install -y \
    python3-setuptools \
    gcc \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install paho-mqtt -i https://pypi.python.org/simple
RUN pip3 install rpi.gpio -i https://pypi.python.org/simple

ADD publish.py /var/jumajumo/publish.py
RUN chmod +x /var/jumajumo/publish.py

CMD python3 /var/jumajumo/publish.py

