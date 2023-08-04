from flask import Flask 
#from analitic.helper import forecast, forecastText, forecastDaily 
from bybitWork import *
# Создание экземпляра Flask приложения
app = Flask(__name__)

@app.route('/stocks')
def stoks():
    stock = stocks_list()
    return stock

@app.route('/stocks/<int:stockId>/coins/<string:coin>/price')
def get_price_now(stockId,coin):
    #BTCUSD

    if stockId == 1:
        priceNow = get_price_now_ByBit(coin)
    else:
        raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return priceNow

# /stocks/$stockId/coins/$coin/priceDaily/$from/$to
@app.route('/stocks/<int:stockId>/coins/<string:coin>/priceDaily/<string:startDate>/<string:endDate>')
def get_prices(stockId,coin, startDate, endDate):
    #2023-01-01','2023-01-03'
    if stockId == 1:
        prices= history_price_coin(coin,startDate,endDate)
    else:
        raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return prices


# Запуск приложения
if __name__ == '__main__':
    # 0000 позволяет получать запросы не только по localhost
    app.run(host='0.0.0.0')