from datetime import datetime, timedelta
#import workYDB
import redis
import json
#sql = workYDB.Ydb()
#from analitic.workBinance import get_BTC_analit_for
#from chat import GPT
from dotenv import load_dotenv
import os
load_dotenv()

#gpt = GPT()
#GPT.set_key(os.getenv('KEY_AI'))


#datetime
def time_epoch():
    from time import mktime
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return int(millis_since_epoch)

def get_dates(day):
    # Текущая дата
    #patern = '2023-07-18T20:26:32'
    patern = '%Y-%m-%dT%H:%M:%S'
    current_date = datetime.now().strftime(patern)

    # Дата, отстоящая на 30 дней
    delta = timedelta(days=day)
    future_date = (datetime.now() + delta).strftime(patern)

    return current_date, future_date

#YDB
def get_model_url(modelName: str):
    modelUrl = sql.select_query('model', f'model = "{modelName}"')[0]['url']
    print('a', modelUrl)
    return modelUrl.decode('utf-8')

def add_message_to_history(userID:str, role:str, message:str):
    mess = {'role': role, 'content': message}
    r.lpush(userID, json.dumps(mess))

def get_history(userID:str):
    items = r.lrange(userID, 0, -1)
    history = [json.loads(m.decode("utf-8")) for m in items[::-1]]
    return history

def clear_history(userID:str):
    r.delete(userID)

# any
def sum_dict_values(dict1, dict2):
    result = {}

    for key in dict1:
        if key in dict2:
            result[key] = dict1[key] + dict2[key]
        else:
            result[key] = dict1[key]

    for key in dict2:
        if key not in dict1:
            result[key] = dict2[key]

    return result


if __name__ == '__main__':
    pass