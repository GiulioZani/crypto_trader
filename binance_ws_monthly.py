from unicorn_binance_websocket_api.unicorn_binance_websocket_api_manager import BinanceWebSocketApiManager
import logging
import time
import threading
import os
from pretty_print import pprint
import json
from settings import settings
from bunch import Bunch

# https://docs.python.org/3/library/logging.html#logging-levels
logging.basicConfig(level=logging.DEBUG,
                    filename=os.path.basename(__file__) + '.log',
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

class MarketData:
    def __init__(self, symbol):
        self.symbol = symbol
        self.bid = None
        self.bid_quantity = None
        self.ask = None
        self.ask_quantity = None

    def __str__(self):
        return str(self.__dict__)

class BinanceWS:
    def __init__(self, update_interval = 1.0):
        # create instance of BinanceWebSocketApiManager for Binance.com Futures
        binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com-futures")

        market_symbols = [m.binance_symbol for m in settings.markets]
        market_symbols = ['BNBUSD']
        self.market_data = {ms:MarketData(ms) for ms in market_symbols}
        binance_websocket_api_manager.create_stream(["bookTicker"], market_symbols, stream_label='BNBUSDT_CURRENT_MONTH@bookTicker_1s')
        def update(binance_websocket_api_manager):
            while True:
                if binance_websocket_api_manager.is_manager_stopping():
                    exit(0)
                oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()

                if oldest_stream_data_from_stream_buffer is False:
                    time.sleep(update_interval)
                else:
                    response = Bunch(json.loads(oldest_stream_data_from_stream_buffer))
                    if 'data' in response:
                        if 'bookTicker' in response['stream']:
                            self.market_data[response.data.s].ask = float(response.data.a)
                            self.market_data[response.data.s].bid = float(response.data.b)
                            self.market_data[response.data.s].bid_quantity = float(response.data.B)
                            self.market_data[response.data.s].ask_quantity = float(response.data.A)

        self.worker_thread = threading.Thread(target=update, args=(binance_websocket_api_manager,))
        self.worker_thread.start()

    def stop(self):
        self.worker_thread.stop()


if __name__ == '__main__':
    binance_ws = BinanceWS()
    import time
    while True:
        print(binance_ws.market_data['BNBUSD'])
        time.sleep(2)

