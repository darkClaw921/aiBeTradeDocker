from flask import Flask 
#from analitic.helper import forecast, forecastText, forecastDaily 
# Создание экземпляра Flask приложения
from traiderWork import get_prognoz 
app = Flask(__name__)

#GET /history
@app.route('/history', methods=['GET'])
def get_history_prognoz():
    rez = get_prognoz()
    return rez


# #POST /strategies/$name/signals
# @app.route('/strategies/<string:name>/signal', methods=['POST'])
# def get_strategie_signal(name):
#     pass



# # GET /strategies/$name/actions/$stockId/$coin
# @app.route('/strategies/<string:name>/actions/<int:stockID>/<string:coin>', methods=['GET'])
# def get_strategie_signal(name, stockID, coin):
#     pass






# Запуск приложения
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5004')
    # 0000 позволяет получать запросы не только по localhost