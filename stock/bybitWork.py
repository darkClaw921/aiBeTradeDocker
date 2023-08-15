from dotenv import load_dotenv
import os
from pybit.unified_trading import HTTP
from pprint import pprint
import requests
from datetime import datetime, timedelta
from helper import time_epoch, get_dates
from workYDB import Ydb
from loguru import logger

load_dotenv()
api_key = os.environ.get('bybit_api')
api_secret =os.environ.get('bybit_secret') 

sql = Ydb()

session = HTTP(
        testnet=False,
        api_key=api_key,
        api_secret=api_secret,
    )



#GET /stocks/$stockId/coins/$coin/price
def get_price_now_ByBit(coin:str='BTCUSD'):
    #symbol = 'BTCUSD'  # Торговая пара: BTC/USD
# Вызов API для получения текущей цены
    url = f'https://api.bybit.com/v2/public/tickers?symbol={coin}'
    response = requests.get(url)
    data = response.json()

    # Извлечение текущей цены из ответа API
    price = data['result'][0]['last_price']

    print(f'Текущая цена {coin}: {price}')
    con = {"price": price}
    return con

def get_price_ByBit(date, coin, interval='D'):
    url = "https://api.bybit.com/v2/public/kline/list"
    params = {
        #"symbol": "BTCUSD",
        "symbol": coin,
        "interval": interval,
        "from": int(datetime.strptime(date, "%Y-%m-%d").timestamp()),
        "limit": 1,
        "reverse": False
    }
    response = requests.get(url, params=params)
    #pprint(response.text)
    data = response.json()["result"][0]

    return {"date": datetime.fromtimestamp(data["open_time"]).strftime("%Y-%m-%d"), "price": data["open"]}

def get_price_ByBit_interval_60m(date, coin, interval='60')->list:
    #интервал в секундах
    url = "https://api.bybit.com/v2/public/kline/list"
    params = {
        #"symbol": "BTCUSD",
        "symbol": coin,
        "interval": interval,
        #"interval": "60",
        "from": int(datetime.strptime(date, "%Y-%m-%d").timestamp()),
        "limit": 24,
        "reverse": False
    }
    response = requests.get(url, params=params)
    #pprint(response.text)
    #data = response.json()["result"][0]
    data = response.json()["result"]
    r = []
    for dat in data:
        r.append({"date": datetime.fromtimestamp(dat["open_time"]).strftime("%Y-%m-%d %H:%m") , "price": dat["open"]})
    return r


def get_prices_ByBit(coin:str, start_date:str, end_date:str, ):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)
    dates = []

    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start += delta

    prices = []
    for date in dates:
        prices.append(get_price_ByBit(date, coin, ))
    
    return prices

def get_prices_ByBit_interval(coin:str, start_date:str, end_date:str, interval)->list:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)
    dates = []

    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start += delta

    prices = []
    for date in dates:
        prices.append(get_price_ByBit_interval_60m(date, coin, interval))
    
    return prices

#GET /stocks/$stockId/coins/$coin/priceDaily/$from/$to
def history_price_coin(coin:str,startDate:str,endDate:str, ):
    history = get_prices_ByBit(coin, startDate,endDate, )
    return history

#GET /orders/$id
def info_order(orderID):
    
    #currency_pair = sql.get_currency_pair(orderID)
    # order = sql.select_query('order',f'orderID={orderID}')[0]
    # print(f'{order=}')
    

    #from pybit.unified_trading import HTTP
    # orderInfo = session.get_order_history(
    #     category=order['category'].decode('utf-8'),
    #     limit=1,
    #     orderId=orderID
    # )
    orderInfo = session.get_order_history(
        category='spot',
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
         'status': orderInfo['orderStatus']}
    logger.info(r)

    sql.update_query('order', row, f'orderID = "{orderID}"') 
    return r


#POST /orders
@logger.catch
def create_order(order):
   # Input
# {
# 'stock': 'byibe',# название биржи
# 'coin': 'btc',# название токена
# 'amount': 10,# количество токенов
# 'mode': 'buy | sell',# режим ордера (купить, продать)
# }
    print(f'{order=}')
    print(f'{order["price"]=}')
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
    
    print(f'create order id {created["result"]["orderId"]}')
    # r = {'id': created.id,
    #      'stock': 'Gate',
    #      'coin': created.currency_pair,
    #      'amount': created.amount,
    #      'mode': created.side,
    #      'state': created.status}

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
        'date_open': get_dates(0)[0]+'Z',
        'price_open': get_price_now_ByBit()['price'],
        'status': 'Open',
        'orderID': created['result']['orderId'],
        'side': order['mode'],
        'need_price_close': price,
        'stock_id': 1,
        'category':'spot',
    }
    sql.insert_query('order', row)
    return row
    

#DELETE /orders/$id
def close_order(orderID):
    order = sql.select_query('order',f'orderID="{orderID}"')[0]
    print(f'{order=}')

    close = session.cancel_order(
        category=order['category'].decode('utf-8'),
        symbol=order['currency_pair'].decode('utf-8'),
        orderId=order['orderID'].decode('utf-8'),
    )
    

    row = {
        'status': 'Cancelled',
        'date_close': get_dates(0)[0]+'Z',
        'price_close': get_price_now_ByBit()['price'] 
    }

    sql.update_query('order', row, f'orderID = "{orderID}"')
    body = {'body': f"Ордер {close['result']['orderId']} был отозван"}
    #return f'Ордер {close.id} был отозван', 200
    return body
#create order id {'retCode': 0, 'retMsg': 'OK', 'result': {'orderId': '1487885204187037440', 'orderLinkId': '1692105738118917'}, 'retExtInfo': {}, 'time': 1692105738128}


if __name__ == '__main__':
    pass
    # delete_order(1487913031129153280)
    # close = session.cancel_order(
    #     category='spot',
    #     symbol='BTCUSTD',
    #     orderId='1487916687522062848',
    # )
    # print(close)
    # 1/0
    # r =  {
# 'stock': 'byibe',# название биржи
# 'coin': 'BTCUSDT',# название токена
# 'amount': '0.004',# количество токенов
# 'mode': 'buy',# режим ордера (купить, продать)
# 'price': '100',
# } 
#     b = set_order(r)
#     print(f'{b=}')

#     a = get_order_info(b['orderID'])
#     print(a)

#     a = delete_order(b['orderID'])
#     print(a)
