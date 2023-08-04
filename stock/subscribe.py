import websocket
import json
from dotenv import load_dotenv
import os
load_dotenv()


api_key = os.environ.get('4T9EYRrFEiCqp71t2l')
api_secret = os.environ.get('uFVFGW6RVrFF9aJDxKoBW9eLyYVJRomiZsXv') 

def on_message(ws, message):
    data = json.loads(message)
    if 'websocket' in data:
        if 'event' in data and data['event'] == 'order':
            # Обработка данных об изменении ордера
            print(data['websocket']['order'])

    elif 'success' in data and data['success']:
        # Успешное подключение к WebSocket API
        print('Соединение WebSocket установлено')

def on_error(ws, error):
    print(f'Ошибка WebSocket: {error}')

def on_close(ws):
    print('WebSocket соединение закрыто')

def on_open(ws):
    print('WebSocket соединение открыто')
    # Подписка на события об изменении ордера
    ws.send(json.dumps({
        'op': 'subscribe',
        'args': ['order']
    }))

websocket.enableTrace(True)

# Формирование подписки на специфичные данные учетной записи
subscription_data = {
    'op': 'auth',
    'args': [api_key, api_secret]
}

ws = websocket.WebSocketApp("wss://stream.bybit.com/realtime",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            on_open=on_open)
ws.on_open = lambda ws: ws.send(json.dumps(subscription_data))
ws.run_forever()


# import websocket
# import json

# def on_message(ws, message):
#     data = json.loads(message)
#     if 'websocket' in data:
#         if 'event' in data and data['event'] == 'order':
#             # Обработка данных об изменении ордера
#             print(data['websocket']['order'])

#     elif 'success' in data and data['success']:
#         # Успешное подключение к WebSocket API
#         print('Соединение WebSocket установлено')

# def on_error(ws, error):
#     print(f'Ошибка Websocket: {error}')

# def on_close(ws):
#     print('WebSocket соединение закрыто')

# def on_open(ws):
#     print('WebSocket соединение открыто')
#     # Подписка на события об изменении ордера
#     ws.send(json.dumps({
#         'op': 'subscribe',
#         'args': ['order']
#     }))

# websocket.enableTrace(True)
# ws = websocket.WebSocketApp("wss://stream.bybit.com/realtime",
#                             on_message=on_message,
#                             on_error=on_error,
#                             on_close=on_close,
#                             on_open=on_open)
# ws.run_forever()