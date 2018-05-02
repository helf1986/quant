#!/usr/bin/env python
# coding=utf-8

import hashlib
import hmac
import requests
import six
import time

from operator import itemgetter

import json
import threading

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.error import ReactorAlreadyRunning

if six.PY2:
    from urllib import urlencode
elif six.PY3:
    from urllib.parse import urlencode


import json
import threading

from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketClientProtocol, connectWS
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.error import ReactorAlreadyRunning

API_URL = 'https://api.binance.com/api'
WITHDRAW_API_URL = 'https://api.binance.com/wapi'
WEBSITE_URL = 'https://www.binance.com'
STREAM_URL = 'wss://stream.binance.com:9443/'

PUBLIC_API_VERSION = 'v1'
PRIVATE_API_VERSION = 'v3'
WITHDRAW_API_VERSION = 'v3'

SYMBOL_TYPE_SPOT = 'SPOT'

ORDER_STATUS_NEW = 'NEW'
ORDER_STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
ORDER_STATUS_FILLED = 'FILLED'
ORDER_STATUS_CANCELED = 'CANCELED'
ORDER_STATUS_PENDING_CANCEL = 'PENDING_CANCEL'
ORDER_STATUS_REJECTED = 'REJECTED'
ORDER_STATUS_EXPIRED = 'EXPIRED'

KLINE_INTERVAL_1MINUTE = '1m'
KLINE_INTERVAL_3MINUTE = '3m'
KLINE_INTERVAL_5MINUTE = '5m'
KLINE_INTERVAL_15MINUTE = '15m'
KLINE_INTERVAL_30MINUTE = '30m'
KLINE_INTERVAL_1HOUR = '1h'
KLINE_INTERVAL_2HOUR = '2h'
KLINE_INTERVAL_4HOUR = '4h'
KLINE_INTERVAL_6HOUR = '6h'
KLINE_INTERVAL_8HOUR = '8h'
KLINE_INTERVAL_12HOUR = '12h'
KLINE_INTERVAL_1DAY = '1d'
KLINE_INTERVAL_3DAY = '3d'
KLINE_INTERVAL_1WEEK = '1w'
KLINE_INTERVAL_1MONTH = '1M'

SIDE_BUY = 'BUY'
SIDE_SELL = 'SELL'

ORDER_TYPE_LIMIT = 'LIMIT'
ORDER_TYPE_MARKET = 'MARKET'
ORDER_TYPE_STOP_LOSS = 'STOP_LOSS'
ORDER_TYPE_STOP_LOSS_LIMIT = 'STOP_LOSS_LIMIT'
ORDER_TYPE_TAKE_PROFIT = 'TAKE_PROFIT'
ORDER_TYPE_TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
ORDER_TYPE_LIMIT_MAKER = 'LIMIT_MAKER'

TIME_IN_FORCE_GTC = 'GTC'  # Good till cancelled
TIME_IN_FORCE_IOC = 'IOC'  # Immediate or cancel
TIME_IN_FORCE_FOK = 'FOK'  # Fill or kill

ORDER_RESP_TYPE_ACK = 'ACK'
ORDER_RESP_TYPE_RESULT = 'RESULT'
ORDER_RESP_TYPE_FULL = 'FULL'

WEBSOCKET_DEPTH_1 = '1'
WEBSOCKET_DEPTH_5 = '5'
WEBSOCKET_DEPTH_10 = '10'
WEBSOCKET_DEPTH_20 = '20'


class BinanceClient(object):


    def __init__(self, api_key, api_secret):
        """Binance API Client constructor

        :param api_key: Api Key
        :type api_key: str.
        :param api_secret: Api Secret
        :type api_secret: str.

        """

        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()

        # init DNS and SSL cert
        self.ping()

    def _init_session(self):

        session = requests.session()
        session.headers.update({'Accept': 'application/json',
                                'User-Agent': 'binance/python',
                                'X-MBX-APIKEY': self.API_KEY})
        return session

    def _create_api_uri(self, path, signed=True, version=PUBLIC_API_VERSION):
        v = PRIVATE_API_VERSION if signed else version
        return API_URL + '/' + v + '/' + path

    def _create_withdraw_api_uri(self, path):
        return WITHDRAW_API_URL + '/' + WITHDRAW_API_VERSION + '/' + path

    def _create_website_uri(self, path):
        return WEBSITE_URL + '/' + path

    def _generate_signature(self, data):

        query_string = urlencode(data)
        m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    def _order_params(self, data):
        """Convert params to list with signature as last element

        :param data:
        :return:

        """
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, value))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    def _request(self, method, uri, signed, force_params=False, **kwargs):

        data = kwargs.get('data', None)
        if data and isinstance(data, dict):
            kwargs['data'] = data
        if signed:
            # generate signature
            kwargs['data']['timestamp'] = int(time.time() * 1000)
            kwargs['data']['signature'] = self._generate_signature(kwargs['data'])

        if data and (method == 'get' or force_params):
            kwargs['params'] = self._order_params(kwargs['data'])
            del(kwargs['data'])

        response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(response)

    def _request_api(self, method, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        uri = self._create_api_uri(path, signed, version)

        return self._request(method, uri, signed, **kwargs)

    def _request_withdraw_api(self, method, path, signed=False, **kwargs):
        uri = self._create_withdraw_api_uri(path)

        return self._request(method, uri, signed, True, **kwargs)

    def _request_website(self, method, path, signed=False, **kwargs):

        uri = self._create_website_uri(path)

        return self._request(method, uri, signed, **kwargs)

    def _handle_response(self, response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status_code).startswith('2'):
            raise BinanceAPIException(response)
        try:
            return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)

    def _get(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('get', path, signed, version, **kwargs)

    def _post(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('post', path, signed, version, **kwargs)

    def _put(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('put', path, signed, version, **kwargs)

    def _delete(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('delete', path, signed, version, **kwargs)

    # Exchange Endpoints

    def get_products(self):
        """Return list of products currently listed on Binance

        Use get_exchange_info() call instead

        :returns: list - List of product dictionaries

        :raises: BinanceResponseException, BinanceAPIException

        """

        products = self._request_website('get', 'exchange/public/product')
        return products

    def get_exchange_info(self):
        """Return rate limits and list of symbols

        :returns: list - List of product dictionaries

        .. code-block:: python

            {
                "timezone": "UTC",
                "serverTime": 1508631584636,
                "rateLimits": [
                    {
                        "rateLimitType": "REQUESTS",
                        "interval": "MINUTE",
                        "limit": 1200
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "SECOND",
                        "limit": 10
                    },
                    {
                        "rateLimitType": "ORDERS",
                        "interval": "DAY",
                        "limit": 100000
                    }
                ],
                "exchangeFilters": [],
                "symbols": [
                    {
                        "symbol": "ETHBTC",
                        "status": "TRADING",
                        "baseAsset": "ETH",
                        "baseAssetPrecision": 8,
                        "quoteAsset": "BTC",
                        "quotePrecision": 8,
                        "orderTypes": ["LIMIT", "MARKET"],
                        "icebergAllowed": false,
                        "filters": [
                            {
                                "filterType": "PRICE_FILTER",
                                "minPrice": "0.00000100",
                                "maxPrice": "100000.00000000",
                                "tickSize": "0.00000100"
                            }, {
                                "filterType": "LOT_SIZE",
                                "minQty": "0.00100000",
                                "maxQty": "100000.00000000",
                                "stepSize": "0.00100000"
                            }, {
                                "filterType": "MIN_NOTIONAL",
                                "minNotional": "0.00100000"
                            }
                        ]
                    }
                ]
            }

        :raises: BinanceResponseException, BinanceAPIException

        """

        return self._get('exchangeInfo')

    def get_symbol_info(self, symbol):
        """Return information about a symbol

        :param symbol: required e.g BNBBTC
        :type symbol: str

        :returns: Dict if found, None if not

        .. code-block:: python

            {
                "symbol": "ETHBTC",
                "status": "TRADING",
                "baseAsset": "ETH",
                "baseAssetPrecision": 8,
                "quoteAsset": "BTC",
                "quotePrecision": 8,
                "orderTypes": ["LIMIT", "MARKET"],
                "icebergAllowed": false,
                "filters": [
                    {
                        "filterType": "PRICE_FILTER",
                        "minPrice": "0.00000100",
                        "maxPrice": "100000.00000000",
                        "tickSize": "0.00000100"
                    }, {
                        "filterType": "LOT_SIZE",
                        "minQty": "0.00100000",
                        "maxQty": "100000.00000000",
                        "stepSize": "0.00100000"
                    }, {
                        "filterType": "MIN_NOTIONAL",
                        "minNotional": "0.00100000"
                    }
                ]
            }

        :raises: BinanceResponseException, BinanceAPIException

        """

        res = self._get('exchangeInfo')

        for item in res['symbols']:
            if item['symbol'] == symbol.upper():
                return item

        return None

    # General Endpoints

    def ping(self):
        """Test connectivity to the Rest API.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#test-connectivity

        :returns: Empty array

        .. code-block:: python

            {}

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('ping')

    def get_server_time(self):
        """Test connectivity to the Rest API and get the current server time.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#check-server-time

        :returns: Current server time

        .. code-block:: python

            {
                "serverTime": 1499827319559
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('time')

    # Market Data Endpoints

    def get_all_tickers(self):
        """Latest price for all symbols.

        https://www.binance.com/restapipub.html#symbols-price-ticker

        :returns: List of market tickers

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "price": "4.00000200"
                },
                {
                    "symbol": "ETHBTC",
                    "price": "0.07946600"
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('ticker/allPrices')

    def get_orderbook_tickers(self):
        """Best price/qty on the order book for all symbols.

        https://www.binance.com/restapipub.html#symbols-order-book-ticker

        :returns: List of order book market entries

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "bidPrice": "4.00000000",
                    "bidQty": "431.00000000",
                    "askPrice": "4.00000200",
                    "askQty": "9.00000000"
                },
                {
                    "symbol": "ETHBTC",
                    "bidPrice": "0.07946700",
                    "bidQty": "9.00000000",
                    "askPrice": "100000.00000000",
                    "askQty": "1000.00000000"
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('ticker/allBookTickers')

    def get_order_book(self, **params):
        """Get the Order Book for the market

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#order-book

        :param symbol: required
        :type symbol: str
        :param limit:  Default 100; max 100
        :type limit: int

        :returns: API response

        .. code-block:: python

            {
                "lastUpdateId": 1027024,
                "bids": [
                    [
                        "4.00000000",     # PRICE
                        "431.00000000",   # QTY
                        []                # Can be ignored
                    ]
                ],
                "asks": [
                    [
                        "4.00000200",
                        "12.00000000",
                        []
                    ]
                ]
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('depth', data=params)

    def get_recent_trades(self, **params):
        """Get recent trades (up to last 500).

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#recent-trades-list

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 500.
        :type limit: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('trades', data=params)

    def get_historical_trades(self, **params):
        """Get older trades.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#recent-trades-list

        :param symbol: required
        :type symbol: str
        :param limit:  Default 500; max 500.
        :type limit: int
        :param fromId:  TradeId to fetch from. Default gets most recent trades.
        :type fromId: str

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "time": 1499865549590,
                    "isBuyerMaker": true,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('historicalTrades', data=params)

    def get_aggregate_trades(self, **params):
        """Get compressed, aggregate trades. Trades that fill at the time,
        from the same order, with the same price will have the quantity aggregated.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#compressedaggregate-trades-list

        :param symbol: required
        :type symbol: str
        :param fromId:  ID to get aggregate trades from INCLUSIVE.
        :type fromId: str
        :param startTime: Timestamp in ms to get aggregate trades from INCLUSIVE.
        :type startTime: int
        :param endTime: Timestamp in ms to get aggregate trades until INCLUSIVE.
        :type endTime: int
        :param limit:  Default 500; max 500.
        :type limit: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "a": 26129,         # Aggregate tradeId
                    "p": "0.01633102",  # Price
                    "q": "4.70443515",  # Quantity
                    "f": 27781,         # First tradeId
                    "l": 27781,         # Last tradeId
                    "T": 1498793709153, # Timestamp
                    "m": true,          # Was the buyer the maker?
                    "M": true           # Was the trade the best price match?
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('aggTrades', data=params)

    def get_klines(self, **params):
        """Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#klinecandlestick-data

        :param symbol: required
        :type symbol: str
        :param interval: -
        :type interval: enum
        :param limit: - Default 500; max 500.
        :type limit: int
        :param startTime:
        :type startTime: int
        :param endTime:
        :type endTime: int

        :returns: API response

        .. code-block:: python

            [
                [
                    1499040000000,      # Open time
                    "0.01634790",       # Open
                    "0.80000000",       # High
                    "0.01575800",       # Low
                    "0.01577100",       # Close
                    "148976.11427815",  # Volume
                    1499644799999,      # Close time
                    "2434.19055334",    # Quote asset volume
                    308,                # Number of trades
                    "1756.87402397",    # Taker buy base asset volume
                    "28.46694368",      # Taker buy quote asset volume
                    "17928899.62484339" # Can be ignored
                ]
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('klines', data=params)

    def get_ticker(self, **params):
        """24 hour price change statistics.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics

        :param symbol:
        :type symbol: str

        :returns: API response

        .. code-block:: python

            {
                "priceChange": "-94.99999800",
                "priceChangePercent": "-95.960",
                "weightedAvgPrice": "0.29628482",
                "prevClosePrice": "0.10002000",
                "lastPrice": "4.00000200",
                "bidPrice": "4.00000000",
                "askPrice": "4.00000200",
                "openPrice": "99.00000000",
                "highPrice": "100.00000000",
                "lowPrice": "0.10000000",
                "volume": "8913.30000000",
                "openTime": 1499783499040,
                "closeTime": 1499869899040,
                "fristId": 28385,   # First tradeId
                "lastId": 28460,    # Last tradeId
                "count": 76         # Trade count
            }

        OR

        .. code-block:: python

            [
                {
                    "priceChange": "-94.99999800",
                    "priceChangePercent": "-95.960",
                    "weightedAvgPrice": "0.29628482",
                    "prevClosePrice": "0.10002000",
                    "lastPrice": "4.00000200",
                    "bidPrice": "4.00000000",
                    "askPrice": "4.00000200",
                    "openPrice": "99.00000000",
                    "highPrice": "100.00000000",
                    "lowPrice": "0.10000000",
                    "volume": "8913.30000000",
                    "openTime": 1499783499040,
                    "closeTime": 1499869899040,
                    "fristId": 28385,   # First tradeId
                    "lastId": 28460,    # Last tradeId
                    "count": 76         # Trade count
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('ticker/24hr', data=params)

    def get_symbol_ticker(self, **params):
        """Latest price for a symbol or symbols.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics

        :param symbol:
        :type symbol: str

        :returns: API response

        .. code-block:: python

            {
                "symbol": "LTCBTC",
                "price": "4.00000200"
            }

        OR

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "price": "4.00000200"
                },
                {
                    "symbol": "ETHBTC",
                    "price": "0.07946600"
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('ticker/price', data=params, version=PRIVATE_API_VERSION)

    def get_orderbook_ticker(self, **params):
        """Latest price for a symbol or symbols.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#symbol-order-book-ticker

        :param symbol:
        :type symbol: str

        :returns: API response

        .. code-block:: python

            {
                "symbol": "LTCBTC",
                "bidPrice": "4.00000000",
                "bidQty": "431.00000000",
                "askPrice": "4.00000200",
                "askQty": "9.00000000"
            }

        OR

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "bidPrice": "4.00000000",
                    "bidQty": "431.00000000",
                    "askPrice": "4.00000200",
                    "askQty": "9.00000000"
                },
                {
                    "symbol": "ETHBTC",
                    "bidPrice": "0.07946700",
                    "bidQty": "9.00000000",
                    "askPrice": "100000.00000000",
                    "askQty": "1000.00000000"
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('ticker/bookTicker', data=params, version=PRIVATE_API_VERSION)

    # Account Endpoints

    def create_order(self, **params):
        """Send in a new order

        Any order with an icebergQty MUST have timeInForce set to GTC.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#new-order--trade

        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: enum
        :param type: required
        :type type: enum
        :param timeInForce: required if limit order
        :type timeInForce: enum
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum

        :returns: API response

        Response ACK:

        .. code-block:: python

            {
                "symbol":"LTCBTC",
                "orderId": 1,
                "clientOrderId": "myOrder1" # Will be newClientOrderId
                "transactTime": 1499827319559
            }

        Response RESULT:

        .. code-block:: python

            {
                "symbol": "BTCUSDT",
                "orderId": 28,
                "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                "transactTime": 1507725176595,
                "price": "0.00000000",
                "origQty": "10.00000000",
                "executedQty": "10.00000000",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "SELL"
            }

        Response FULL:

        .. code-block:: python

            {
                "symbol": "BTCUSDT",
                "orderId": 28,
                "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
                "transactTime": 1507725176595,
                "price": "0.00000000",
                "origQty": "10.00000000",
                "executedQty": "10.00000000",
                "status": "FILLED",
                "timeInForce": "GTC",
                "type": "MARKET",
                "side": "SELL",
                "fills": [
                    {
                        "price": "4000.00000000",
                        "qty": "1.00000000",
                        "commission": "4.00000000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3999.00000000",
                        "qty": "5.00000000",
                        "commission": "19.99500000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3998.00000000",
                        "qty": "2.00000000",
                        "commission": "7.99600000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3997.00000000",
                        "qty": "1.00000000",
                        "commission": "3.99700000",
                        "commissionAsset": "USDT"
                    },
                    {
                        "price": "3995.00000000",
                        "qty": "1.00000000",
                        "commission": "3.99500000",
                        "commissionAsset": "USDT"
                    }
                ]
            }

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        return self._post('order', True, data=params)

    def order_limit(self, timeInForce=TIME_IN_FORCE_GTC, **params):
        """Send in a new limit order

        Any order with an icebergQty MUST have timeInForce set to GTC.

        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: enum
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: decimal
        :param timeInForce: default Good till cancelled
        :type timeInForce: enum
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with LIMIT, STOP_LOSS_LIMIT, and TAKE_PROFIT_LIMIT to create an iceberg order.
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'type': ORDER_TYPE_LIMIT,
            'timeInForce': timeInForce
        })
        return self.create_order(**params)


    def order_limit_buy(self, timeInForce=TIME_IN_FORCE_GTC, **params):
        """Send in a new limit buy order

        Any order with an icebergQty MUST have timeInForce set to GTC.

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: decimal
        :param timeInForce: default Good till cancelled
        :type timeInForce: enum
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param stopPrice: Used with stop orders
        :type stopPrice: decimal
        :param icebergQty: Used with iceberg orders
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': SIDE_BUY,
        })
        return self.order_limit(timeInForce=timeInForce, **params)


    def order_limit_sell(self, timeInForce=TIME_IN_FORCE_GTC, **params):
        """Send in a new limit sell order

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: decimal
        :param timeInForce: default Good till cancelled
        :type timeInForce: enum
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param stopPrice: Used with stop orders
        :type stopPrice: decimal
        :param icebergQty: Used with iceberg orders
        :type icebergQty: decimal

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': SIDE_SELL
        })
        return self.order_limit(timeInForce=timeInForce, **params)


    def order_market(self, **params):
        """Send in a new market order

        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: enum
        :param quantity: required
        :type quantity: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'type': ORDER_TYPE_MARKET
        })
        return self.create_order(**params)


    def order_market_buy(self, **params):
        """Send in a new market buy order

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': SIDE_BUY
        })
        return self.order_market(**params)


    def order_market_sell(self, **params):
        """Send in a new market sell order

        :param symbol: required
        :type symbol: str
        :param quantity: required
        :type quantity: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum

        :returns: API response

        See order endpoint for full response options

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException

        """
        params.update({
            'side': SIDE_SELL
        })
        return self.order_market(**params)


    def create_test_order(self, **params):
        """Test new order creation and signature/recvWindow long. Creates and validates a new order but does not send it into the matching engine.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#test-new-order-trade

        :param symbol: required
        :type symbol: str
        :param side: required
        :type side: enum
        :param type: required
        :type type: enum
        :param timeInForce: required if limit order
        :type timeInForce: enum
        :param quantity: required
        :type quantity: decimal
        :param price: required
        :type price: decimal
        :param newClientOrderId: A unique id for the order. Automatically generated if not sent.
        :type newClientOrderId: str
        :param icebergQty: Used with iceberg orders
        :type icebergQty: decimal
        :param newOrderRespType: Set the response JSON. ACK, RESULT, or FULL; default: RESULT.
        :type newOrderRespType: enum
        :param recvWindow: The number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {}

        :raises: BinanceResponseException, BinanceAPIException, BinanceOrderException, BinanceOrderMinAmountException, BinanceOrderMinPriceException, BinanceOrderMinTotalException, BinanceOrderUnknownSymbolException, BinanceOrderInactiveSymbolException


        """
        return self._post('order/test', True, data=params)


    def get_order(self, **params):
        """Check an order's status. Either orderId or origClientOrderId must be sent.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#query-order-user_data

        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :param origClientOrderId: optional
        :type origClientOrderId: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "symbol": "LTCBTC",
                "orderId": 1,
                "clientOrderId": "myOrder1",
                "price": "0.1",
                "origQty": "1.0",
                "executedQty": "0.0",
                "status": "NEW",
                "timeInForce": "GTC",
                "type": "LIMIT",
                "side": "BUY",
                "stopPrice": "0.0",
                "icebergQty": "0.0",
                "time": 1499827319559
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('order', True, data=params)


    def get_all_orders(self, **params):
        """Get all account orders; active, canceled, or filled.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#all-orders-user_data

        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :param limit: Default 500; max 500.
        :type limit: int
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1",
                    "price": "0.1",
                    "origQty": "1.0",
                    "executedQty": "0.0",
                    "status": "NEW",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": "BUY",
                    "stopPrice": "0.0",
                    "icebergQty": "0.0",
                    "time": 1499827319559
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('allOrders', True, data=params)


    def cancel_order(self, **params):
        """Cancel an active order. Either orderId or origClientOrderId must be sent.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#cancel-order-trade

        :param symbol: required
        :type symbol: str
        :param orderId: The unique order id
        :type orderId: int
        :param origClientOrderId: optional
        :type origClientOrderId: str
        :param newClientOrderId: Used to uniquely identify this cancel. Automatically generated by default.
        :type newClientOrderId: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "symbol": "LTCBTC",
                "origClientOrderId": "myOrder1",
                "orderId": 1,
                "clientOrderId": "cancelMyOrder1"
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._delete('order', True, data=params)

    def get_open_orders(self, **params):
        """Get all open orders on a symbol.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#current-open-orders-user_data

        :param symbol: required
        :type symbol: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "symbol": "LTCBTC",
                    "orderId": 1,
                    "clientOrderId": "myOrder1",
                    "price": "0.1",
                    "origQty": "1.0",
                    "executedQty": "0.0",
                    "status": "NEW",
                    "timeInForce": "GTC",
                    "type": "LIMIT",
                    "side": "BUY",
                    "stopPrice": "0.0",
                    "icebergQty": "0.0",
                    "time": 1499827319559
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('openOrders', True, data=params)

    # User Stream Endpoints
    def get_account(self, **params):
        """Get current account information. 账户持仓情况

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-information-user_data

        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "makerCommission": 15,
                "takerCommission": 15,
                "buyerCommission": 0,
                "sellerCommission": 0,
                "canTrade": true,
                "canWithdraw": true,
                "canDeposit": true,
                "balances": [
                    {
                        "asset": "BTC",
                        "free": "4723846.89208129",
                        "locked": "0.00000000"
                    },
                    {
                        "asset": "LTC",
                        "free": "4763368.68006011",
                        "locked": "0.00000000"
                    }
                ]
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('account', True, data=params)

    def get_my_trades(self, **params):
        """Get trades for a specific symbol.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#account-trade-list-user_data

        :param symbol: required
        :type symbol: str
        :param limit: Default 500; max 500.
        :type limit: int
        :param fromId: TradeId to fetch from. Default gets most recent trades.
        :type fromId: int
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            [
                {
                    "id": 28457,
                    "price": "4.00000100",
                    "qty": "12.00000000",
                    "commission": "10.10000000",
                    "commissionAsset": "BNB",
                    "time": 1499865549590,
                    "isBuyer": true,
                    "isMaker": false,
                    "isBestMatch": true
                }
            ]

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._get('myTrades', True, data=params)

    # Withdraw Endpoints

    def withdraw(self, **params):
        """Submit a withdraw request.

        https://www.binance.com/restapipub.html

        Assumptions:

        - You must have Withdraw permissions enabled on your API key
        - You must have withdrawn to the address specified through the website and approved the transaction via email

        :param asset: required
        :type asset: str
        :type address: required
        :type address: str
        :param amount: required
        :type amount: decimal
        :param name: Description of the address - optional
        :type name: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "msg": "success",
                "success": true
            }

        :raises: BinanceResponseException, BinanceAPIException, BinanceWithdrawException

        """
        res = self._request_withdraw_api('post', 'withdraw.html', True, data=params)
        if not res['success']:
            raise BinanceWithdrawException(res['msg'])
        return res

    def get_deposit_history(self, **params):
        """Fetch deposit history.

        https://www.binance.com/restapipub.html

        :param asset: optional
        :type asset: str
        :type status: 0(0:pending,1:success) optional
        :type status: int
        :param startTime: optional
        :type startTime: long
        :param endTime: optional
        :type endTime: long
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "depositList": [
                    {
                        "insertTime": 1508198532000,
                        "amount": 0.04670582,
                        "asset": "ETH",
                        "status": 1
                    }
                ],
                "success": true
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._request_withdraw_api('get', 'depositHistory.html', True, data=params)

    def get_withdraw_history(self, **params):
        """Fetch withdraw history.

        https://www.binance.com/restapipub.html

        :param asset: optional
        :type asset: str
        :type status: 0(0:Email Sent,1:Cancelled 2:Awaiting Approval 3:Rejected 4:Processing 5:Failure 6Completed) optional
        :type status: int
        :param startTime: optional
        :type startTime: long
        :param endTime: optional
        :type endTime: long
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "withdrawList": [
                    {
                        "amount": 1,
                        "address": "0x6915f16f8791d0a1cc2bf47c13a6b2a92000504b",
                        "asset": "ETH",
                        "applyTime": 1508198532000
                        "status": 4
                    },
                    {
                        "amount": 0.005,
                        "address": "0x6915f16f8791d0a1cc2bf47c13a6b2a92000504b",
                        "txId": "0x80aaabed54bdab3f6de5868f89929a2371ad21d666f20f7393d1a3389fad95a1",
                        "asset": "ETH",
                        "applyTime": 1508198532000,
                        "status": 4
                    }
                ],
                "success": true
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._request_withdraw_api('get', 'withdrawHistory.html', True, data=params)

    def get_deposit_address(self, **params):
        """Fetch a deposit address for a symbol

        https://www.binance.com/restapipub.html

        :param asset: required
        :type asset: str
        :param recvWindow: the number of milliseconds the request is valid for
        :type recvWindow: int

        :returns: API response

        .. code-block:: python

            {
                "address": "0x6915f16f8791d0a1cc2bf47c13a6b2a92000504b",
                "success": true,
                "addressTag": "1231212",
                "asset": "BNB"
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._request_withdraw_api('get', 'depositAddress.html', True, data=params)

    # User Stream Endpoints

    def stream_get_listen_key(self):
        """Start a new user data stream and return the listen key
        If a stream already exists it should return the same key.
        If the stream becomes invalid a new key is returned.

        Can be used to keep the user stream alive.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#start-user-data-stream-user_stream

        :returns: API response

        .. code-block:: python

            {
                "listenKey": "pqia91ma19a5s61cv6a81va65sdf19v8a65a1a5s61cv6a81va65sdf19v8a65a1"
            }

        :raises: BinanceResponseException, BinanceAPIException

        """
        res = self._post('userDataStream', False, data={})
        return res['listenKey']

    def stream_keepalive(self, **params):
        """PING a user data stream to prevent a time out.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#keepalive-user-data-stream-user_stream

        :param listenKey: required
        :type listenKey: str

        :returns: API response

        .. code-block:: python

            {}

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._put('userDataStream', False, data=params)

    def stream_close(self, **params):
        """Close out a user data stream.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#close-user-data-stream-user_stream

        :returns: API response

        .. code-block:: python

            {}

        :raises: BinanceResponseException, BinanceAPIException

        """
        return self._delete('userDataStream', False, data=params)


class DepthCache(object):

    def __init__(self, symbol):
        """Intialise the DepthCache

        :param symbol: Symbol to create depth cache for
        :type symbol: string

        """
        self.symbol = symbol
        self._bids = {}
        self._asks = {}

    def add_bid(self, bid):
        """Add a bid to the cache

        :param bid:
        :return:

        """
        self._bids[bid[0]] = float(bid[1])
        if bid[1] == "0.00000000":
            del self._bids[bid[0]]

    def add_ask(self, ask):
        """Add an ask to the cache

        :param ask:
        :return:

        """
        self._asks[ask[0]] = float(ask[1])
        if ask[1] == "0.00000000":
            del self._asks[ask[0]]

    def get_bids(self):
        """Get the current bids

        :return: list of bids with price and quantity as floats

        .. code-block:: python

            [
                [
                    0.0001946,  # Price
                    45.0        # Quantity
                ],
                [
                    0.00019459,
                    2384.0
                ],
                [
                    0.00019158,
                    5219.0
                ],
                [
                    0.00019157,
                    1180.0
                ],
                [
                    0.00019082,
                    287.0
                ]
            ]

        """
        return DepthCache.sort_depth(self._bids, reverse=True)

    def get_asks(self):
        """Get the current asks

        :return: list of asks with price and quantity as floats

        .. code-block:: python

            [
                [
                    0.0001955,  # Price
                    57.0'       # Quantity
                ],
                [
                    0.00019699,
                    778.0
                ],
                [
                    0.000197,
                    64.0
                ],
                [
                    0.00019709,
                    1130.0
                ],
                [
                    0.0001971,
                    385.0
                ]
            ]

        """
        return DepthCache.sort_depth(self._asks, reverse=False)

    @staticmethod
    def sort_depth(vals, reverse=False):
        """Sort bids or asks by price
        """
        lst = [[float(price), quantity] for price, quantity in vals.items()]
        lst = sorted(lst, key=itemgetter(0), reverse=reverse)
        return lst


class DepthCacheManager(object):

    def __init__(self, client, symbol, callback):
        """Intialise the DepthCacheManager

        :param client: Binance API client
        :type client: binance.Client
        :param symbol: Symbol to create depth cache for
        :type symbol: string
        :param callback: Function to receive depth cache updates
        :type callback: function

        """
        self._client = client
        self._symbol = symbol
        self._callback = callback
        self._first_update_id = 0
        self._bm = None
        self._depth_cache = DepthCache(self._symbol)

        self._init_cache()
        self._start_socket()

    def _init_cache(self):
        res = self._client.get_order_book(symbol=self._symbol, limit=500)

        self._first_update_id = res['lastUpdateId']

        for bid in res['bids']:
            self._depth_cache.add_bid(bid)
        for ask in res['asks']:
            self._depth_cache.add_ask(ask)

    def _start_socket(self):
        self._bm = BinanceSocketManager(self._client)

        self._bm.start_depth_socket(self._symbol, self._depth_event)

        self._bm.start()

    def _depth_event(self, msg):
        """

        :param msg:
        :return:

        """
        # ignore any updates before the initial update id
        if msg['u'] <= self._first_update_id:
            return

        # add any bid or ask values
        for bid in msg['b']:
            self._depth_cache.add_bid(bid)
        for ask in msg['a']:
            self._depth_cache.add_ask(ask)

        # call the callback with the updated depth cache
        self._callback(self._depth_cache)

    def get_depth_cache(self):
        """Get the current depth cache

        :return: DepthCache object

        """
        return self._depth_cache

    def close(self):
        """Close the open socket for this manager

        :return:
        """
        self._bm.close()


class BinanceClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        # reset the delay after reconnecting
        self.factory.resetDelay()

    def onMessage(self, payload, isBinary):
        if not isBinary:
            try:
                payload_obj = json.loads(payload.decode('utf8'))
            except ValueError:
                pass
            else:
                self.factory.callback(payload_obj)


class BinanceReconnectingClientFactory(ReconnectingClientFactory):

    # set initial delay to a short time
    initialDelay = 0.1

    maxDelay = 10

    maxRetries = 5


class BinanceClientFactory(WebSocketClientFactory, BinanceReconnectingClientFactory):

    protocol = BinanceClientProtocol

    def clientConnectionFailed(self, connector, reason):
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        # check if closed cleanly
        if reason.getErrorMessage() != 'Connection was closed cleanly.':
            self.retry(connector)


class BinanceSocketManager(threading.Thread):

    _user_timeout = 30 * 60  # 30 minutes

    def __init__(self, client):
        """Initialise the BinanceSocketManager

        :param client: Binance API client
        :type client: binance.Client

        """
        threading.Thread.__init__(self)
        self._conns = {}
        self._user_timer = None
        self._user_listen_key = None
        self._user_callback = None
        self._client = client

    def _start_socket(self, path, callback, prefix='ws/'):
        if path in self._conns:
            return False

        factory_url = STREAM_URL + prefix + path
        factory = BinanceClientFactory(factory_url)
        factory.protocol = BinanceClientProtocol
        factory.callback = callback
        context_factory = ssl.ClientContextFactory()

        self._conns[path] = connectWS(factory, context_factory)
        return path

    def start_depth_socket(self, symbol, callback, depth=WEBSOCKET_DEPTH_1):
        """Start a websocket for symbol market depth

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#partial-book-depth-streams

        :param symbol: required
        :type symbol: str
        :param callback: callback function to handle messages
        :type callback: function
        :param depth: Number of depth entries to return, default WEBSOCKET_DEPTH_1
        :type depth: enum

        :returns: connection key string if successful, False otherwise

        Message Format

        .. code-block:: python

            {
                "e": "depthUpdate",			# event type
                "E": 1499404630606, 		# event time
                "s": "ETHBTC", 				# symbol
                "u": 7913455, 				# updateId to sync up with updateid in /api/v1/depth
                "b": [						# bid depth delta
                    [
                        "0.10376590", 		# price (need to update the quantity on this price)
                        "59.15767010", 		# quantity
                        []					# can be ignored
                    ],
                ],
                "a": [						# ask depth delta
                    [
                        "0.10376586", 		# price (need to update the quantity on this price)
                        "159.15767010", 	# quantity
                        []					# can be ignored
                    ],
                    [
                        "0.10383109",
                        "345.86845230",
                        []
                    ],
                    [
                        "0.10490700",
                        "0.00000000", 		# quantity=0 means remove this level
                        []
                    ]
                ]
            }
        """
        socket_name = symbol.lower() + '@depth'
        if depth != WEBSOCKET_DEPTH_1:
            socket_name = '{}{}'.format(socket_name, depth)
        return self._start_socket(socket_name, callback)

    def start_kline_socket(self, symbol, callback, interval=BinanceClient.KLINE_INTERVAL_1MINUTE):
        """Start a websocket for symbol kline data

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams

        :param symbol: required
        :type symbol: str
        :param callback: callback function to handle messages
        :type callback: function
        :param interval: Kline interval, default KLINE_INTERVAL_1MINUTE
        :type interval: enum

        :returns: connection key string if successful, False otherwise

        Message Format

        .. code-block:: python

            {
                "e": "kline",					# event type
                "E": 1499404907056,				# event time
                "s": "ETHBTC",					# symbol
                "k": {
                    "t": 1499404860000, 		# start time of this bar
                    "T": 1499404919999, 		# end time of this bar
                    "s": "ETHBTC",				# symbol
                    "i": "1m",					# interval
                    "f": 77462,					# first trade id
                    "L": 77465,					# last trade id
                    "o": "0.10278577",			# open
                    "c": "0.10278645",			# close
                    "h": "0.10278712",			# high
                    "l": "0.10278518",			# low
                    "v": "17.47929838",			# volume
                    "n": 4,						# number of trades
                    "x": false,					# whether this bar is final
                    "q": "1.79662878",			# quote volume
                    "V": "2.34879839",			# volume of active buy
                    "Q": "0.24142166",			# quote volume of active buy
                    "B": "13279784.01349473"	# can be ignored
                    }
            }
        """
        socket_name = '{}@kline_{}'.format(symbol.lower(), interval)
        return self._start_socket(socket_name, callback)

    def start_trade_socket(self, symbol, callback):
        """Start a websocket for symbol trade data

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#trade-streams

        :param symbol: required
        :type symbol: str
        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        Message Format

        .. code-block:: python

            {
                "e": "trade",     # Event type
                "E": 123456789,   # Event time
                "s": "BNBBTC",    # Symbol
                "t": 12345,       # Trade ID
                "p": "0.001",     # Price
                "q": "100",       # Quantity
                "b": 88,          # Buyer order Id
                "a": 50,          # Seller order Id
                "T": 123456785,   # Trade time
                "m": true,        # Is the buyer the market maker?
                "M": true         # Ignore.
            }

        """
        return self._start_socket(symbol.lower() + '@trade', callback)

    def start_aggtrade_socket(self, symbol, callback):
        """Start a websocket for symbol trade data

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#aggregate-trade-streams

        :param symbol: required
        :type symbol: str
        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        Message Format

        .. code-block:: python

            {
                "e": "aggTrade",		# event type
                "E": 1499405254326,		# event time
                "s": "ETHBTC",			# symbol
                "a": 70232,				# aggregated tradeid
                "p": "0.10281118",		# price
                "q": "8.15632997",		# quantity
                "f": 77489,				# first breakdown trade id
                "l": 77489,				# last breakdown trade id
                "T": 1499405254324,		# trade time
                "m": false,				# whether buyer is a maker
                "M": true				# can be ignored
            }

        """
        return self._start_socket(symbol.lower() + '@aggTrade', callback)

    def start_symbol_ticker_socket(self, symbol, callback):
        """Start a websocket for a symbol's ticker data

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#individual-symbol-ticker-streams

        :param symbol: required
        :type symbol: str
        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        Message Format

        .. code-block:: python

            {
                "e": "24hrTicker",  # Event type
                "E": 123456789,     # Event time
                "s": "BNBBTC",      # Symbol
                "p": "0.0015",      # Price change
                "P": "250.00",      # Price change percent
                "w": "0.0018",      # Weighted average price
                "x": "0.0009",      # Previous day's close price
                "c": "0.0025",      # Current day's close price
                "Q": "10",          # Close trade's quantity
                "b": "0.0024",      # Best bid price
                "B": "10",          # Bid bid quantity
                "a": "0.0026",      # Best ask price
                "A": "100",         # Best ask quantity
                "o": "0.0010",      # Open price
                "h": "0.0025",      # High price
                "l": "0.0010",      # Low price
                "v": "10000",       # Total traded base asset volume
                "q": "18",          # Total traded quote asset volume
                "O": 0,             # Statistics open time
                "C": 86400000,      # Statistics close time
                "F": 0,             # First trade ID
                "L": 18150,         # Last trade Id
                "n": 18151          # Total number of trades
            }

        """
        return self._start_socket(symbol.lower() + '@ticker', callback)

    def start_ticker_socket(self, callback):
        """Start a websocket for all ticker data

        By default all markets are included in an array.

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#all-market-tickers-stream

        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        Message Format

        .. code-block:: python

            [
                {
                    'F': 278610,
                    'o': '0.07393000',
                    's': 'BCCBTC',
                    'C': 1509622420916,
                    'b': '0.07800800',
                    'l': '0.07160300',
                    'h': '0.08199900',
                    'L': 287722,
                    'P': '6.694',
                    'Q': '0.10000000',
                    'q': '1202.67106335',
                    'p': '0.00494900',
                    'O': 1509536020916,
                    'a': '0.07887800',
                    'n': 9113,
                    'B': '1.00000000',
                    'c': '0.07887900',
                    'x': '0.07399600',
                    'w': '0.07639068',
                    'A': '2.41900000',
                    'v': '15743.68900000'
                }
            ]
        """
        return self._start_socket('!ticker@arr', callback)

    def start_multiplex_socket(self, streams, callback):
        """Start a multiplexed socket using a list of socket names.
        User stream sockets can not be included.

        Symbols in socket name must be lowercase i.e bnbbtc@aggTrade, neobtc@ticker

        Combined stream events are wrapped as follows: {"stream":"<streamName>","data":<rawPayload>}

        https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md

        :param streams: list of stream names in lower case
        :type streams: list
        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        Message Format - see Binance API docs for all types

        """
        stream_path = 'streams={}'.format('/'.join(streams))
        return self._start_socket(stream_path, callback, 'stream?')

    def start_user_socket(self, callback):
        """Start a websocket for user data

        https://www.binance.com/restapipub.html#user-wss-endpoint

        :param callback: callback function to handle messages
        :type callback: function

        :returns: connection key string if successful, False otherwise

        Message Format - see Binance API docs for all types
        """
        if self._user_listen_key:
            # cleanup any sockets with this key
            for conn_key in self._conns:
                if len(conn_key) >= 60 and conn_key[:60] == self._user_listen_key:
                    self.stop_socket(conn_key)
                    break
        self._user_listen_key = self._client.stream_get_listen_key()
        self._user_callback = callback
        conn_key = self._start_socket(self._user_listen_key, callback)
        if conn_key:
            # start timer to keep socket alive
            self._start_user_timer()

        return conn_key

    def _start_user_timer(self):
        self._user_timer = threading.Timer(self._user_timeout, self._keepalive_user_socket)
        self._user_timer.setDaemon(True)
        self._user_timer.start()

    def _keepalive_user_socket(self):
        listen_key = self._client.stream_get_listen_key()
        # check if they key changed and
        if listen_key != self._user_listen_key:
            self.start_user_socket(self._user_callback)
        self._start_user_timer()

    def stop_socket(self, conn_key):
        """Stop a websocket given the connection key

        :param conn_key: Socket connection key
        :type conn_key: string

        :returns: connection key string if successful, False otherwise
        """
        if conn_key not in self._conns:
            return

        self._conns[conn_key].disconnect()
        del(self._conns[conn_key])

        # check if we have a user stream socket
        if len(conn_key) >= 60 and conn_key[:60] == self._user_listen_key:
            self._stop_user_socket()

    def _stop_user_socket(self):
        if not self._user_listen_key:
            return
        # stop the timer
        self._user_timer.cancel()
        self._user_timer = None
        # close the stream
        self._client.stream_close(listenKey=self._user_listen_key)
        self._user_listen_key = None

    def run(self):
        try:
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            # Ignore error about reactor already running
            pass

    def close(self):
        """Close all connections

        """
        keys = set(self._conns.keys())
        for key in keys:
            self.stop_socket(key)

        self._conns = {}



class BinanceAPIException(Exception):

    LISTENKEY_NOT_EXIST = '-1125'

    def __init__(self, response):
        json_res = response.json()
        self.status_code = response.status_code
        self.response = response
        self.code = json_res['code']
        self.message = json_res['msg']
        self.request = getattr(response, 'request', None)

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)


class BinanceRequestException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'BinanceRequestException: %s' % self.message


class BinanceOrderException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'BinanceOrderException(code=%s): %s' % (self.code, self.message)


class BinanceOrderMinAmountException(BinanceOrderException):

    def __init__(self, value):
        message = "Amount must be a multiple of %s" % value
        super(BinanceOrderMinAmountException, self).__init__(-1013, message)


class BinanceOrderMinPriceException(BinanceOrderException):

    def __init__(self, value):
        message = "Price must be at least %s" % value
        super(BinanceOrderMinPriceException, self).__init__(-1013, message)


class BinanceOrderMinTotalException(BinanceOrderException):

    def __init__(self, value):
        message = "Total must be at least %s" % value
        super(BinanceOrderMinTotalException, self).__init__(-1013, message)


class BinanceOrderUnknownSymbolException(BinanceOrderException):

    def __init__(self, value):
        message = "Unknown symbol %s" % value
        super(BinanceOrderUnknownSymbolException, self).__init__(-1013, message)


class BinanceOrderInactiveSymbolException(BinanceOrderException):

    def __init__(self, value):
        message = "Attempting to trade an inactive symbol %s" % value
        super(BinanceOrderInactiveSymbolException, self).__init__(-1013, message)


class BinanceWithdrawException(Exception):
    def __init__(self, message):
        if message == u'参数异常':
            message = 'Withdraw to this address through the website first'
        self.message = message

    def __str__(self):
        return 'BinanceWithdrawException: %s' % self.message