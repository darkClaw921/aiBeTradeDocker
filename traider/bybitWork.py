from dotenv import load_dotenv
import os
from pybit.unified_trading import HTTP
from pprint import pprint
import requests
from datetime import datetime, timedelta

load_dotenv()
api_key = os.environ.get('bybit_api')
api_secret =os.environ.get('bybit_secret') 

session = HTTP(
    testnet=False,
    api_key=api_key,
    api_secret=api_secret,
)
# Get the orderbook of the USDT Perpetual, BTCUSDT
a = session.get_orderbook(category="linear", symbol="BTCUSDT")
print(a)

# print(session.place_order(
#     category="inverse",
#     symbol="ETHUSD",
#     side="Sell",
#     orderType="Market",
#     qty=1,
# ))
#GET /stocks/
def stocks_list():
    stocks = [{
        "id": 1,
        "name":"ByBit", # Название биржи
        "url": "https://www.bybit.com/",# главная страница биржи
        "apiUrl": "https://bybit-exchange.github.io/docs/category/derivatives" #// Путь к API биржи
    }]

    return stocks 

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

def get_price_ByBit(date, coin):
    url = "https://api.bybit.com/v2/public/kline/list"
    params = {
        #"symbol": "BTCUSD",
        "symbol": coin,
        "interval": "D",
        "from": int(datetime.strptime(date, "%Y-%m-%d").timestamp()),
        "limit": 1,
        "reverse": False
    }
    response = requests.get(url, params=params)
    #pprint(response.text)
    data = response.json()["result"][0]
    return {"date": datetime.fromtimestamp(data["open_time"]).strftime("%Y-%m-%d"), "price": data["open"]}

def get_prices_ByBit(coin:str, start_date:str, end_date:str):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)
    dates = []

    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start += delta

    prices = []
    for date in dates:
        prices.append(get_price_ByBit(date, coin))
    
    return prices

#GET /stocks/$stockId/coins/$coin/priceDaily/$from/$to
def history_price_coin(coin:str,startDate:str,endDate:str):
    history = get_prices_ByBit(coin, startDate,endDate)
    return history


# Create five long USDC Options orders.
# (Currently, only USDC Options support sending orders in bulk.)
payload = {"category": "option"}
orders = {
  "symbol": "BTCUSDT",
  "side": "Buy",
  "orderType": "Limit",
  "qty": "0.1",
  "price": '10',
}
print(session.place_order(
    category="inverse",
    symbol="BTCUSDT",
    side="Sell",
    orderType="Limit",
    qty='0.1',
    price= '10'
)) 

#payload["request"] = orders
# Submit the orders in bulk.
session.place_batch_order(orders)

if __name__ == '__main__':
    pass
    #pprint(a)
    #a = get_price_coin()
    #a = get_btc_prices('2023-01-01','2023-01-03')
    #a = get_btc_price("2023-01-01")
    #print(a) 
#     category="linear",
#     symbol="BTCUSDT",
#     side="Buy",
#     orderType="Market",
#     qty=0.001,
# ))