from bitmex_ws import BitMEXWebsocket
from binance.websockets import BinanceSocketManager
from binance.client import Client
import bitmex
import subprocess
import requests
import numpy as np
import time
import json
import sys
from pretty_print import pprint
import threading
import traceback
from settings import settings
from binance_ws import BinanceWS
from collections import namedtuple
import ipdb

# TODO:
# - FIX DECIMALS
# - fix yifi
# - fix does not make orders


def approximately_equal(value1, value2, relative_threshold):
    #import pdb; pdb.set_trace()
    return np.abs(value1 - value2) <= relative_threshold * value1


Offer = namedtuple('Offer', ['price', 'quantity'])


class Trader(threading.Thread):
    def get_volatility(self):
        pass

    def get_decimals(self, number):
        return len(str(number).split('.')[1])

    def get_bid_ask(self):
        bitmex_response = self.bitmex_ws.get_ticker()
        return {
            'binance_ask': self.binance_ws_data.ask,
            'bitmex_ask': bitmex_response['sell'],
            'binance_bid': self.binance_ws_data.bid,
            'bitmex_bid': bitmex_response['buy']
        }

    def get_bid_ask_rest(self):
        response = self.bitmex_client.OrderBook.OrderBook_getL2(
            symbol=self.bitmex_symbol, depth=100).result()[0]
        bitmex_bid = max([r['price'] for r in response if r['side'] == 'Buy'])
        bitmex_ask = min([r['price'] for r in response if r['side'] == 'Sell'])

        response = self.binance_client.get_order_book(
            symbol=self.binance_symbol)
        binance_ask = response['asks'][0][0]
        binance_bid = response['bids'][0][0]
        return {
            'binance_ask': float(binance_ask),
            'binance_bid': float(binance_bid),
            'bitmex_ask': float(bitmex_ask),
            'bitmex_bid': float(bitmex_bid)
        }

    ## TODO: fix this to not cancel order uselessly
    def get_order_id(self, price):
        orders = self.bitmex_client.Order.Order_getOrders(
            filter=json.dumps({
                'open': True,
                'price': price,
                'symbol': self.bitmex_symbol
            })).result()[0]
        return orders[0]['orderID'] if len(orders) > 0 else None

    def cancel_order(self, order_id):
        self.bitmex_client.Order.Order_cancel(orderID=order_id).result()

    def cancel_order_by_price_if_exists(self, price):
        order_id = self.get_order_id(price)
        if order_id is not None:
            self.cancel_order(order_id)
            print('Canceled existing order')

    def cancel_all_orders(self):
        orders = self.bitmex_client.Order.Order_getOrders(
            filter=json.dumps({
                'open': True,
                'symbol': self.bitmex_symbol
            })).result()[0]
        print("About to cancel", len(orders))
        for order in orders:
            self.bitmex_client.Order.Order_cancel(
                orderID=order["orderID"]).result()

    def compare_offers(self, price, quantity, offer):
        return approximately_equal(
            offer['price'], price,
            self.relative_threshold) and quantity == offer['orderQty']

    def cancel_order_by_id(self, order_id):
        if order_id != '':
            result = self.bitmex_client.Order.Order_cancel(
                orderID=order_id).result()[0]
            return result

    def make_offer(self, offer, hidden=True):
        result = None
        side = 'buy' if offer.quantity >= 0 else 'sell'
        if approximately_equal(
                self.last_offers[side].price, offer.price,
                self.equality_threshold) and \
                self.last_offers[side].quantity == offer.quantity:
            print(
                f'Omitted unnecessary order \n last: {self.last_offers[side]} current: {offer} ({side})'
            )
        else:
            print(
                f'About to make order \n last: {self.last_offers[side]} current: {offer} ({side})'
            )
            # self.cancel_order_by_price_if_exists(self.last_offers[side])
            self.cancel_order_by_id(self.last_order_id)
            result = self.bitmex_client.Order.Order_new(
                symbol=self.bitmex_symbol,
                # ordType="Limit",
                orderQty=offer.quantity,
                price=round(offer.price, self.decimals - 1),
                displayQty=int(not hidden),
            ).result()[0]
            self.last_order_id = result['orderID']
        self.last_offers[side] = offer
        return result

    def get_orders_and_positions_rest(self):
        response = self.bitmex_client.Position.Position_get(
            filter=json.dumps({'symbol': self.bitmex_symbol})).result()[0]
        if len(response) > 0:
            return response[0]['currentQty']
        else:
            return 0

    def get_orders_and_positions(self):
        """
        response = self.bitmex_client.Position.Position_get(filter=json.dumps({'symbol':self.bitmex_symbol})).result()[0]
        if len(response) > 0:
            return response[0]['currentQty']
        else:
            return 0
        """
        # ipdb.set_trace()
        return self.bitmex_ws.positions()[0]['currentQty']

    def get_buy_offer_price(
        self,
        bid_asks,
    ):
        price = None
        if bid_asks['bitmex_bid'] < bid_asks['binance_bid'] * (
                1 - self.margin_trigger):
            print("Buy condition met")
            price = bid_asks['bitmex_bid'] + self.overprice
        else:
            print("Buy: Fallback")
            price = bid_asks[
                'binance_bid'] * self.relative_fallback_underprice  #es: 0.9 quindi 90%
        return round(price, self.decimals)

    def get_sell_offer_price(
        self,
        bid_asks,
    ):
        price = None
        if bid_asks['bitmex_ask'] > bid_asks['binance_ask'] * (
                1 - self.margin_trigger):
            print('Sell condition met')
            price = bid_asks['bitmex_ask'] - self.underprice
        else:
            print("Fallback")
            price = bid_asks[
                'binance_bid'] * self.relative_fallback_overprice  # 1.1 quindi 110%
        return round(price, self.decimals)

    def run(self):
        try:
            print(f'\nSymbol: {self.binance_symbol}')
            orders_and_positions = self.get_orders_and_positions_rest()
            print('Our balance is: ', orders_and_positions)
            asks_bids = self.get_bid_ask_rest()
            print(asks_bids)
            if orders_and_positions < self.balance_threshold:
                buy_offer_price = self.get_buy_offer_price(asks_bids)
                buy_quantity = self.balance_threshold - orders_and_positions
                if buy_quantity > 0:
                    self.make_offer(
                        Offer(buy_offer_price, buy_quantity),
                        hidden=True,
                    )
            else:
                print('Nothing to buy')
            sell_offer_price = self.get_sell_offer_price(asks_bids)
            if orders_and_positions > 0:
                self.make_offer(
                    Offer(sell_offer_price, -orders_and_positions),
                    hidden=True,
                )
            else:
                print('Nothing to sell')
        except Exception as e:
            print('An exception occurred')
            print(e)
            traceback.print_exc()
            time.sleep(3.0)

    def __init__(self, bitmex_client, binance_client, binance_ws_data, params):
        self.binance_ws_data = binance_ws_data
        self.bitmex_client = bitmex_client
        self.binance_client = binance_client
        self.bitmex_symbol = params['bitmex_symbol']
        self.binance_symbol = params['binance_symbol']
        self.underprice = params.get('underprice', None)
        self.overprice = params.get('overprice', None)
        self.balance_threshold = params.get('balance_threshold', 5)
        self.fills_changed = params.get('fills_changed', lambda _: None)
        self.margin_trigger = params.get('margin_trigger', 0.01)
        asks_bids = self.get_bid_ask_rest()
        self.decimals = params.get(
            'decimals',
            max(self.get_decimals(asks_bids['bitmex_bid']),
                self.get_decimals(asks_bids['bitmex_ask']), 3))
        self.relative_fallback_overprice = params.get(
            'relative_fallback_overprice', 1.1)
        self.relative_fallback_underprice = params.get(
            'relative_fallback_underprice', 0.9)
        self.fallback_equality_threshold = params.get(
            'fallback_equality_threshold', 0.05)
        self.equality_threshold = params.get('equality_threshold',
                                             0.0003)  # == 0.02%/100
        if self.underprice is None:
            self.underprice = 10**(-self.decimals + 3) / 2.0
        if self.overprice is None:
            self.overprice = 10**(-self.decimals + 3) / 2.0
        print(f"\nInitializing {self.binance_symbol}")
        print(f"Underprice: {self.underprice}\nOverprice: {self.overprice}")
        print('decimals', self.decimals)
        self.bitmex_ws = BitMEXWebsocket(
            endpoint="https://testnet.bitmex.com/api/v1",
            symbol=self.
            bitmex_symbol,  #[t['bitmex_symbol'] for t in settings['trades']][:-1],
            api_key=settings.auth.bitmex_key,
            api_secret=settings.auth.bitmex_secret)
        self.last_offers = {
            'buy': Offer(-100.0, -100.0),
            'sell': Offer(-100.0, -100.0)
        }
        self.last_order_id = ''
        self.cancel_all_orders()


class TraderManager(threading.Thread):
    def __init__(self, fills_changed=lambda _: None):  # traders_params
        super().__init__()
        self.fills_changed = fills_changed
        bitmex_key = settings.auth.bitmex_key
        bitmex_secret = settings.auth.bitmex_secret
        self.bitmex_client = bitmex.bitmex(test=True,
                                           api_key=bitmex_key,
                                           api_secret=bitmex_secret)

        binance_key = settings.auth.binance_key
        binance_secret = settings.auth.binance_secret
        self.binance_client = Client(binance_key, binance_secret)
        self.binance_ws = BinanceWS()
        self.trader_wait = 1.0
        self.repeat_interval = 10.0
        self.traders = []
        settings.markets = settings.markets[:-1]  # FIXME
        for market in settings.markets:  # per ogni dizionario nella lista
            trader = Trader(self.bitmex_client, self.binance_client,
                            self.binance_ws.market_data[market.binance_symbol],
                            market)
            self.traders.append(trader)
            time.sleep(self.trader_wait)
        self.fills = self.get_fills()

    def get_fills(self):
        #return self.bitmex_client.Execution.Execution_getTradeHistory().result()[0]
        return self.traders[0].bitmex_ws.recent_trades()

    def run(
        self
    ):  # fai finta che sia il start direttamente, quando nel main fai il trader_manager.start() questo metodo viene chiamato
        while True:
            for trader in self.traders:
                trader.run()
                time.sleep(self.trader_wait)

            new_fills = self.get_fills()
            if new_fills != self.fills:
                print('\n### Fills have changed ###')
                changed_fills = [
                    fill for fill in new_fills if fill not in self.fills
                ]
                print(changed_fills)
                ##for trader in traders:
                #    if trader.
                self.fills_changed(changed_fills)
                self.fills = new_fills

            time.sleep(self.repeat_interval -
                       float(len(self.traders)) * self.trader_wait)


# binance inserire futures
# TODO: buy moving average
if __name__ == '__main__':

    def fills_changed(new_fills):
        # viene chiamata quando cambiano le fills
        # manda messaggio telegram ecc.
        print('\t\tFills have changed!!!')
        pprint(new_fills)
        keys = ['symbol', 'price', 'cumQty', 'lastQty', 'side']
        message = ''
        for fill in new_fills:
            data = {key: fill[key] for key in keys}
            message += f"Ciao Alessio! c'e' stato un cambiamento nelle fills:\n{json.dumps(data, indent=4)}\n"
        bash_command = ["telegram-send", "--config", "user.conf", message]
        process = subprocess.Popen(bash_command, stdout=subprocess.PIPE)
        output, error = process.communicate()

    trader_manager = TraderManager(fills_changed=fills_changed)
    trader_manager.start()
