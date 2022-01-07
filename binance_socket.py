from binance.client import Client
from binance.websockets import BinanceSocketManager

import pprint
pp = pprint.PrettyPrinter(indent=4)
pprint = pp.pprint


key = "qZcPoVzc5v7FcGWXiXnZ7ONQxEZEK8wnPTPg06GFpIXl5uRTeu1SxtaTlsZVHPc3"
secret = "tWqUvJ6vCaIuV4ZMCA1X8a01iKD6yjuxY6LBCYW5mBhNKnS5VMhuBPtojlJEcOTg"
client = Client(key, secret)

# set a timeout of 60 seconds
bm = BinanceSocketManager(client, user_timeout=60)

bm = BinanceSocketManager(client)
# start any sockets here, i.e a trade socket

def process_message(msg):
    pprint(msg)

conn_key = bm.start_ticker_socket('BNBUSDT', process_message)
# then start the socket manager
bm.start()

