FROM python

WORKDIR /content

RUN pip install python-binance bitmex unicorn-binance-websocket-api 

ENTRYPOINT python trader.py
