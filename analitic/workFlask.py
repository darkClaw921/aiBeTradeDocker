from flask import Flask 
from analitic.helper import forecast, forecastText, forecastDaily 
# Создание экземпляра Flask приложения
app = Flask(__name__)

@app.route('/')
def home():
    return 'Привет, мир!'

# def forecast(coin:str):

#     return {'price': 12345}

# def forecastDaily(coin:str):
#     return {'price': [12345, 10, 20]}

# def forecastText(coin:str):
#     return {'data': """Дата прогноза: 11/07/23
# Предсказанная стоимость биткоина на 16/07/23: 30410
# Использованные методы:
# 1. Свечной график: Анализ свечей позволяет определить тренды и ключевые уровни поддержки и сопротивления. В данном случае, мы видим, что цена биткоина в последние недели колеблется в узком диапазоне между 29800 и 30700. Это является зоной сопротивления и поддержки соответственно.
# """} http://localhost:3000/stocks/23/coins/btc/sa/2
#http://localhost:3000/stocks/23/coins/btc/sa/2
@app.route('/stocks/<int:stockId>/coins/<string:coin>/<string:func>/<int:days>', methods=['GET'])
def coin(stockId, coin, func, days):
    # Проверка условий или типов параметров
    if days < 1:
        raise ValueError("Days должен быть положительным числом")
    
    if func == 'forecast':
        answer = forecast(days)
        answer = {'price': answer}

    if func == 'forecastDaily':
        answer = forecastDaily(days)
    
    if func == 'forecastText':
        answer = forecastText(days)
    return answer 
    #return f"Stock ID: {stockId}, Coin: {coin}, Function: {func}, Days: {days}"

  

# Запуск приложения
if __name__ == '__main__':
    # 0000 позволяет получать запросы не только по localhost
    app.run(host='0.0.0.0')