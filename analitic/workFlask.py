from flask import Flask 
from helper import forecast, forecastText, forecastDaily 
# Создание экземпляра Flask приложения
app = Flask(__name__)

@app.route('/')
def home():
    return 'Привет, мир!'

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
    #app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port='5001')
    #answer = forecastText(1)
    #print(answer)