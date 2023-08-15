# !/usr/bin/env python
# coding: utf-8
import logging
from decimal import Decimal as D
from dotenv import load_dotenv
import os
from gate_api import ApiClient, Configuration, Order, SpotApi
from loguru import logger
from six.moves.urllib.parse import urlparse
from workYDB import *
from config import RunConfig
from helper import *


from pybit.unified_trading import HTTP
load_dotenv()
# api_key = os.environ.get('gate_api')
# api_secret =os.environ.get('gate_secret') 

api_key = os.environ.get('bybit_api')
api_secret =os.environ.get('bybit_secret')
sql = Ydb()
#logger = logging.getLogger('__name12__')
# logger.add()
session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )
a='a'.title
def create_order(order):
# {
# “stock”: “byibe”, // название биржи
# “coin”: “btc”, // название токена
# “amount”: 10, // количество токенов
# “mode”: “buy | sell”, // режим ордера (купить, продать)
# }

    try:
        price = order['price']
    

        created = session.place_order(
            category="spot",
            symbol="BTCUSDT",
            side= order['mode'].title(),
            orderType="Limit",
            qty=order['amount'],
            price=str(price),
            #timeInForce="PostOnly",
            #orderLinkId="spot-test-postonly",
            #isLeverage=0,
           #orderFilter="Order",
        )
    except:
        price = 0
        created = session.place_order(
            category="spot",
            symbol="BTCUSDT",
            side= order['mode'].title(),
            orderType="Market",
            qty=order['amount'],
            #price="15600",
            #timeInForce="PostOnly",
            #orderLinkId="spot-test-postonly",
            #isLeverage=0,
            #orderFilter="Order",
        ) 
    
    print(f'create order id {created}')
    r = {'id': created.id,
         'stock': 'Gate',
         'coin': created.currency_pair,
         'amount': created.amount,
         'mode': created.side,
         'state': created.status}

    # created = session.place_order(
    #     category="spot",
    #     symbol="BTCUSDT",
    #     side="Buy",
    #     orderType="Market",
    #     #price=29300,
    #     qty=0.0002,
    # )
    
    #{'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': '1487806611478068992', 'orderLinkId': '1692096369139910'}, 'retExtInfo': {}, 'time': 1692096369147}
    row = {
        'time_epoh': time_epoch(),
        'amount': order['amount'],
        'currency_pair' : order['coin'],
        'date_open': get_dates(0)[0],
        'price_open': get_price_now_ByBit(),
        'status': 'Open',
        'orderID': created['result']['orderId'],
        'side': order['mode'],
        'need_price_close': price
    }
    sql.insert_query('order', row)
    return r

def info_order(orderID):
    
    
    #currency_pair = sql.get_currency_pair(orderID)
    order = sql.select_query('order',f'orderID={orderID}')[0]
    print(f'{order=}')
    

    #from pybit.unified_trading import HTTP
    orderInfo = session.get_order_history(
        category=order['category'].decode('utf-8'),
        limit=1,
        orderId=orderID
    )
    logger.info(f'{orderInfo=}')
    orderInfo = orderInfo['result']['list'][0]
    row = {
        'status': orderInfo['orderStatus'], 
    }
    r = {'id': orderInfo['orderId'],
         'stock': 'ByBit',
         'coin': orderInfo['symbol'],
         'amount': orderInfo['qty'],
         'mode': orderInfo['side'],
         'srate': orderInfo['orderStatus']}
    logger.info(r)

    sql.update_query('order', row, f'orderID = {orderID}') 
    return row

@logger.catch
def close_order(orderID):
    order = sql.select_query('order',f'orderID={orderID}')[0]
    print(f'{order=}')

    close = session.cancel_order(
        category=order['category'].decode('utf-8'),
        symbol=order['symbol'].decode('utf-8'),
        orderId=order['orderId'].decode('utf-8'),
    )

    row = {
        'status': 'cancelled',
        'date_close': get_dates(0)[0],
        'price_close': order['price_close']
    }

    sql.update_query('order', row, f'orderID = {orderID}')
    body = {'body': f'Ордер {close.id} был отозван'}
    #return f'Ордер {close.id} был отозван', 200
    return body
    #return close_order

if __name__ == '__main__':
    pass
    #info_order(379767600704)
    #close_order(2)