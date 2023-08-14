from loguru import logger
from workYDB import Ydb
import requests
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv()
sql = Ydb()
STOCK_URL = os.environ.get('STOCK_URL')
def get_prognoz():
    """Создает ордер на основе прогноза из базы"""
    rows = sql.select_query('prognoz', "type='prognoz' and side='SELL'")
    rez = []
    for row in rows:
        print(f'{row=}')


        data = {
            'stock': 'byibe', # название биржи
            'coin': row['currency_pair'].decode('utf-8'), # название токена
            'amount': 0.0001, #количество токенов
            'price': row['price_open'],
            'mode': row['side'].decode('utf-8').lower(), # режим ордера (купить, продать)
        }
        print(data)
        req = requests.post(f'{STOCK_URL}/orders',json=data)
        print(req.text)
        
        date = datetime.fromtimestamp(row['date_open'])
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')

        entity = {'what': row['side'].decode('utf-8').lower(),
                  'when': formatted_date,
                  'why':row['strat'].decode('utf-8')}
        rez.append(entity)
    return rez

if __name__ == '__main__':
    get_prognoz()