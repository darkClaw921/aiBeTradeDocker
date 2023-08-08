from flask import Flask, request, render_template
#from analitic.helper import forecast, forecastText, forecastDaily 
from bybitWork import *
from gateWork import *
# Создание экземпляра Flask приложения
app = Flask(__name__)
def stocks_list():
    stocks = [{
        "id": 1,
        "name":"ByBit", # Название биржи
        "url": "https://www.bybit.com/",# главная страница биржи
        "apiUrl": "https://bybit-exchange.github.io/docs/category/derivatives" ## Путь к API биржи
    }, {
        "id": 2,
        "name":"Gate", # Название биржи
        "url": "gate.io",# главная страница биржи
        "apiUrl": "https://api.gateio.ws/api/v4" ## Путь к API биржи]
    }]
    return stocks 

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

@app.route('/orders/<int:orderID>',methods=['GET'])
def get_order(orderID):
    #2023-01-01','2023-01-03'
    order = info_order(orderID)
    # if stockId == 1:
    #     prices= history_price_coin(coin,startDate,endDate)
    # else:
    #     #TODO добавить проверку если нет в базе такого ордера
    #     # raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return order

@app.route('/orders',methods=['POST'])
def set_order():
    from decimal import Decimal
    #2023-01-01','2023-01-03'
    data = request.get_json() 
    
    data['amount'] = Decimal(data['amount'])
    print(data)
    try:
        order = create_order(data)
    except Exception as e:
        raise ValueError(e)
        #return e
    # if stockId == 1:
    #     prices= history_price_coin(coin,startDate,endDate)
    # else:
    #     #TODO добавить проверку если нет в базе такого ордера
    #     # raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return order
#@app.route('/orders',methods=['POST'])

#DELETE /orders/$id

@app.route('/orders/<int:orderID>',methods=['DELETE'])
@logger.catch
def del_order(orderID):
    #2023-01-01','2023-01-03'

    order = close_order(orderID)
    
        #raise 'ORDER_NOT_FOUND'
    # if stockId == 1:
    #     prices= history_price_coin(coin,startDate,endDate)
    # else:
    #     #TODO добавить проверку если нет в базе такого ордера
    #     # raise ValueError(f'Нет биржы с id {stockId}')
    #stock = stocks_list()
    return order

# @app.errorhandler(Exception)
# def handle_exception(e):
#     # обработка ошибки
#     print(f'++++++++++++++++{e=}')
#     #return render_template('/Users/igorgerasimov/Python/Bitrix/aiBeTradeDocker/stock/error.html', error=str(e)), 500
# #    return render_template('error.html'), 500
#     return e



# Запуск приложения
if __name__ == '__main__':
    # 0000 позволяет получать запросы не только по localhost
    app.run(host='0.0.0.0',port='5001',debug=False)