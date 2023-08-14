from flask import Flask 
#from analitic.helper import forecast, forecastText, forecastDaily 
from bybitWork import *
from strat import add_7d_trends_to_YDB
# Создание экземпляра Flask приложения
from infoStrat import *
app = Flask(__name__)

@app.route('/stocks')
def stoks():
    stock = stocks_list()
    return stock
#GET /strategies/$name/info
@app.route('/strategies/<string:name>/info', methods=['GET'])
def get_strategie_name(name):
   
    return strats[name]


#POST /strategies/$name/signals
@app.route('/strategies/<string:name>/signal', methods=['POST'])
def get_strategie_signal(name):
    pass

# Input
# {
# 	“stockId”: “37”, // id биржи для которой проводится анализ
# 	“coin”: “BTC”, // Код монеты для которой рассматривается стратегия
# 	“start_date”: yyyy-mm-dd, // Начальная дата работы стратегии (если пусто, то сегодня),
# 	“days”: 15, // Время моделирования в днях,
# 	“params”: { // параметры стратегии
# 		“$min_enter_price”: $value1,
# 		“$param2”: $value2,
# }
# }

# GET /strategies/$name/actions/$stockId/$coin
@app.route('/strategies/<string:name>/actions/<int:stockID>/<string:coin>', methods=['GET'])
def get_strategie_prognoz(name, stockID, coin):
    prognoz = add_7d_trends_to_YDB(True)
    return {'body':prognoz, 'status':200}
   

# {
# 	“strategy”: “name of strategy”, 
# “stockId”: “37”, // id биржи для которой проводится анализ
# 	“coin”: “BTC”, // Код монеты для которой рассматривается стратегия
# 	“action”: “none | buy”,
# 	“buyPrice”: 100, // По какой цене сделать покупку
# 	"sellPrice”: 200, // По какой цене выставить продаже
# 	“sellPeriod”: 7 // Сколько дней держать ордер на продажу (максимум).
# }





# Запуск приложения
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5002')
    # 0000 позволяет получать запросы не только по localhost