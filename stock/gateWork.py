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
load_dotenv()
api_key = os.environ.get('gate_api')
api_secret =os.environ.get('gate_secret') 

sql = Ydb()
#logger = logging.getLogger('__name12__')
# logger.add()
class RunConfig(object):

    def __init__(self, api_key=None, api_secret=None, host_used=None):
        # type: (str, str, str) -> None
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_used = host_used
        self.use_test = urlparse(host_used).hostname == "fx-api-testnet.gateio.ws"

def spot_demo(run_config):
    # type: (RunConfig) -> None
    currency_pair = "BTC_USDT"
    currency = currency_pair.split("_")[1]

    # Initialize API client
    # Setting host is optional. It defaults to https://api.gateio.ws/api/v4
    config = Configuration(key=run_config.api_key, secret=run_config.api_secret, host=run_config.host_used)
    spot_api = SpotApi(ApiClient(config))
    pair = spot_api.get_currency_pair(currency_pair)
    logger.info("testing against currency pair: " + currency_pair)
    min_amount = pair.min_base_amount

    # get last price
    tickers = spot_api.list_tickers(currency_pair=currency_pair)
    assert len(tickers) == 1
    last_price = tickers[0].last
    logger.info(f'{last_price}')
    # make sure balance is enough
    order_amount = D(min_amount) * 2
    accounts = spot_api.list_spot_accounts(currency=currency)
    assert len(accounts) == 1
    available = D(accounts[0].available)
    logger.info(f"Account available: {str(available)} {currency}", str(available), currency)
    if available < order_amount:
        logger.error("Account balance not enough")
        return
    1/0
    order = Order(amount=str(order_amount*2), price=last_price, side='sell', currency_pair=currency_pair, type='limit')
    logger.info(f"place a spot {order.side} order in {order.currency_pair} with amount {order.amount} and price {order.price}",)
                
    created = spot_api.create_order(order)
    #close = spot_api.cancel_orders
    #logger.info(f'{close=}')
    logger.info(f"order created with id {created.id}, status {created.status}")
    1/0
    if created.status == 'open':
        order_result = spot_api.get_order(created.id, currency_pair)
        logger.info(f"order {order_result.id} filled {order_result.filled_total}, left: {order_result.left}")
        result = spot_api.cancel_order(order_result.id, currency_pair)
        if result.status == 'cancelled':
            logger.info("order {result.id} cancelled", )
    else:
        trades = spot_api.list_my_trades(currency_pair, order_id=created.id)
        assert len(trades) > 0
        for t in trades:
            logger.info(f"order {t.order_id} filled {t.amount} with price {t.price}")


def create_order(order):

    run_config = RunConfig(api_key,api_secret, 'https://api.gateio.ws/api/v4') 
    config = Configuration(key=run_config.api_key, secret=run_config.api_secret, host=run_config.host_used)
    spot_api = SpotApi(ApiClient(config))
    
    #currency_pair = "BTC_USDT"
    
    currency_pair = order['coin']
    currency = currency_pair.split("_")[1] 
     # get last price
    tickers = spot_api.list_tickers(currency_pair=currency_pair)
    assert len(tickers) == 1
    price_pair = tickers[0].last
    #logger.info(f'{last_price}')
    
    try:
        last_price = order['price']
    except:
        last_price = tickers[0].last
    logger.info(f'{last_price=}')
    # pair = spot_api.get_currency_pair(currency_pair) 
    # min_amount = pair.min_base_amount
    # order_amount = D(min_amount) * 2

    #order = Order(amount=str(order['amount']), price=last_price, side='buy', currency_pair=currency_pair)
    order = Order(amount=str(order['amount']), price=last_price, side=order['mode'], currency_pair=currency_pair)
    logger.info(f"place a spot {order.side} order in {order.currency_pair} with amount {order.amount} and price {order.price}",)
    
    created = spot_api.create_order(order)
    print(f'create order id {created.id}')
    r = {'id': created.id,
         'stock': 'Gate',
         'coin': created.currency_pair,
         'amount': created.amount,
         'mode': created.side,
         'state': created.status}
    
    row = {
        'time_epoh': time_epoch(),
        'amount': created.amount,
        'currency_pair' : created.currency_pair,
        'date_open': get_dates(0)[0],
        'price_open': price_pair,
        'status': created.status,
        'orderID': created.id,
        'side': created.side,
        'need_price_close': created.price
    }
    sql.insert_query('order', row)
    return r

def info_order(orderID):
    
    run_config = RunConfig(api_key,api_secret, 'https://api.gateio.ws/api/v4') 
    config = Configuration(key=run_config.api_key, secret=run_config.api_secret, host=run_config.host_used)
    spot_api = SpotApi(ApiClient(config))
    #currency_pair = "BTC_USDT"
    
    currency_pair = sql.get_currency_pair(orderID)
    

    orderInfo = spot_api.get_order(orderID,currency_pair=currency_pair)
    r = {'id': orderInfo.id,
         'stock': 'Gate',
         'coin': orderInfo.currency_pair,
         'amount': orderInfo.amount,
         'mode': orderInfo.side,
         'srate': orderInfo.status}
    logger.info(r)

    row = {
        'status': orderInfo.status, 
    }

    sql.update_query('order', row, f'orderID = {orderID}') 
    return r

@logger.catch
def close_order(orderID):
    run_config = RunConfig(api_key,api_secret, 'https://api.gateio.ws/api/v4') 
    config = Configuration(key=run_config.api_key, secret=run_config.api_secret, host=run_config.host_used)
    spot_api = SpotApi(ApiClient(config))
    currency_pair = sql.get_currency_pair(orderID) 
    #currency_pair = "BTC_USDT"
    tickers = spot_api.list_tickers(currency_pair=currency_pair)
    assert len(tickers) == 1
    price_pair = tickers[0].last

    close = spot_api.cancel_order(orderID, currency_pair)
    row = {
        'status': 'cancelled',
        'date_close': get_dates(0)[0],
        'price_close': price_pair 
    }

    sql.update_query('order', row, f'orderID = {orderID}')
    body = {'body': f'Ордер {close.id} был отозван'}
    #return f'Ордер {close.id} был отозван', 200
    return body
    #return close_order

if __name__ == '__main__':
    spot_demo(RunConfig(api_key,api_secret, 'https://api.gateio.ws/api/v4'))
    pass
    #close_order(2)