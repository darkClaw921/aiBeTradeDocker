from flask import Flask 
#from analitic.helper import forecast, forecastText, forecastDaily 
from bybitWork import *
# Создание экземпляра Flask приложения
app = Flask(__name__)

@app.route('/stocks')
def stoks():
    stock = stocks_list()
    return stock

@app.route('/stocks/<int:stockId>/coins/<string:coin>/price',methods=['GET'])
def get_price_now(stockId,coin):
    #BTCUSD

    if stockId == 1:
        priceNow = get_price_now_ByBit(coin)
    else:
        raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return priceNow

# /stocks/$stockId/coins/$coin/priceDaily/$from/$to
@app.route('/stocks/<int:stockId>/coins/<string:coin>/priceDaily/<string:startDate>/<string:endDate>',methods=['GET'])
def get_prices(stockId,coin, startDate, endDate):
    #2023-01-01','2023-01-03'
    if stockId == 1:
        prices= history_price_coin(coin,startDate,endDate)
    else:
        raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return prices

@app.route('/orders/<int:id>',methods=['GET'])
def get_order(orderID):
    #2023-01-01','2023-01-03'
    order = get_order_info(orderID)
    # if stockId == 1:
    #     prices= history_price_coin(coin,startDate,endDate)
    # else:
    #     #TODO добавить проверку если нет в базе такого ордера
    #     # raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return order

@app.route('/orders',methods=['POST'])
def create_order(order):
    #2023-01-01','2023-01-03'
    order = set_order(order)
    # if stockId == 1:
    #     prices= history_price_coin(coin,startDate,endDate)
    # else:
    #     #TODO добавить проверку если нет в базе такого ордера
    #     # raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return order
@app.route('/orders',methods=['POST'])

#DELETE /orders/$id
def del_order(orderID):
    #2023-01-01','2023-01-03'
    order = delete_order(orderID)
    # if stockId == 1:
    #     prices= history_price_coin(coin,startDate,endDate)
    # else:
    #     #TODO добавить проверку если нет в базе такого ордера
    #     # raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return order




# Запуск приложения
if __name__ == '__main__':
    # 0000 позволяет получать запросы не только по localhost
    app.run(host='0.0.0.0')