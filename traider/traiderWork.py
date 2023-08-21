from loguru import logger
from workYDB import Ydb
import requests
from dotenv import load_dotenv
from datetime import datetime
from helper import date_now
import os
from pprint import pprint
load_dotenv()
sql = Ydb()
STOCK_URL = os.environ.get('STOCK_URL')
def get_prognoz():
    """Создает ордер на основе прогноза из базы"""
    rows = sql.select_query('prognoz', "type='prognoz' and side='BUY'")
    rez = []

    for row in rows:
        print(f'{row=}')


        data = {
            'stock': 'byibe', # название биржи
            'coin': row['currency_pair'].decode('utf-8'), # название токена
            'amount': 0.000050, #количество токенов
            #'price': str(row['price_open']),
            'price': str(row['price_open']),
            'mode': row['side'].decode('utf-8').title(), # режим ордера (купить, продать)
        }
        print(data)
        
        req = requests.post(f'{STOCK_URL}/orders',json=data)
        print(req.text)
        
        try:
            date = datetime.fromtimestamp(row['date_open'])
        except:
            continue
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')

        entity = {'what': row['side'].decode('utf-8').lower(),
                  'when': formatted_date,
                  'why':row['strat'].decode('utf-8')}
        rez.append(entity)
        r = {
            'type':'in working'
        }
        sql.update_query('prognoz',r,f'time_epoh={row["time_epoh"]}')

    return rez


def a():
    #сработаный ордер на продажу + считаем профит
    rows = sql.select_query('order', "side='Sell' and status='Triggered'")
    
    for row in rows:
        orderID = row['orderID'].decode('utf-8')
        buyOrder = sql.select_query('order',f"link_orderID = '{orderID}'")[0]
        profit = (row['price_close'] - buyOrder['price_open']) * row['amount']

        profitPersent = (row['price_close'] / buyOrder['price_open'])-1
        
        # priceNow =requests.get(f'{STOCK_URL}/stocks/1/coins/BTCUSD/price') 
        # priceNow = float(eval(priceNow.text)['price'])
        
        row1 = {
            'status': 'Done',
            'profit': profit,
            'profit_persent': profitPersent, 
            'date_close': date_now(),

        } 
        pprint(f'{row1=}')
        row2 = {
            'status': 'Done',
        }
        
        sql.update_query('order',row1, f"orderID = '{orderID}'")
        orderID = buyOrder['orderID'].decode('utf-8')
        sql.update_query('order',row2, f"orderID = '{orderID}'")

def sell_order():
    rows = sql.select_query('order', "side='Buy' and status='Triggered'")

    for row in rows:
        print(f'{row=}')


        data = {
            'stock': 'byibe', # название биржи
            'coin': row['currency_pair'].decode('utf-8'), # название токена
            'amount': str(row['amount']),
            'price': str(row['need_price_close']),
            'mode': 'Sell', # режим ордера (купить, продать)
        }
        print(data)
        req = requests.post(f'{STOCK_URL}/orders',json=data)
        rez = eval(req.text)
        print(f'{rez=}')

        row1 = {
            'status': 'on sell',
            'link_orderID': rez['orderID'],
        }
        orderID = row['orderID']
        sql.update_query('order',row1, f"orderID = '{orderID}'")
        
        row1 = {
            'status': rez['status'],
            'link_orderID': row['orderID'],
        } 
        orderID = rez['orderID']
        sql.update_query('order',row1, f"orderID = '{orderID}'")


def check_orders():
    rows = sql.select_query('order', "status IN ('Created', 'Active','New')")
    print(rows)
    
    for row in rows:
        orderID = row['orderID'].decode('utf-8')
        #if date_now - row['date_open']
        req = requests.get(f'{STOCK_URL}/orders/{orderID}',)
        #req = requests.post(f'{STOCK_URL}/stocks',)
        rez = req.text
        print(f'{rez=}')

    
    #sql.update_query('order',row1, f"orderID = '{orderID}'")


if __name__ == '__main__':
    # check_orders()
    a()