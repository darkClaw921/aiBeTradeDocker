from datetime import datetime, timedelta
import workYDB
import redis
import json
from workBinance import get_BTC_analit_for
from chat import GPT
from dotenv import load_dotenv
import os

load_dotenv()
sql = workYDB.Ydb()

gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))


#datetime
def time_epoch():
    from time import mktime
    dt = datetime.now()
    sec_since_epoch = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    millis_since_epoch = sec_since_epoch * 1000
    return int(millis_since_epoch)

def get_dates_YDB(day):
    # Текущая дата
    #patern = '2023-07-18T20:26:32'
    patern = '%Y-%m-%dT%H:%M:%S'
    current_date = datetime.now().strftime(patern)

    # Дата, отстоящая на 30 дней
    delta = timedelta(days=day)
    future_date = (datetime.now() + delta).strftime(patern)

    return current_date, future_date

def get_dates(day):
    # Текущая дата
    current_date = datetime.now().strftime("%d/%m/%Y")

    # Дата, отстоящая на 30 дней
    delta = timedelta(days=day)
    future_date = (datetime.now() + delta).strftime("%d/%m/%Y")

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

def forecastText(day:int):
    promtUrl = 'https://docs.google.com/document/d/1_Ft4sDJJpGdBX8k2Et-OBIUtvO0TSuw8ZSjbv5r7H7I/edit?usp=sharing'
    PROMT_URL = promtUrl 
    #promt = gpt.load_prompt(promptUrl)
    promt = gpt.load_prompt(PROMT_URL)
    #promt = 
    #print(f'{promptUrl=}')
    analitBTC = get_BTC_analit_for(day)
    #print(f'{analitBTC}')
    current, future = get_dates(day)
    
    print("Текущая дата:", current)
    print(f"Дата через {day} дней:", future)
    promt = promt.replace('[analitict]', analitBTC)
    promt = promt.replace('[nextDate]', str(day))
    promt = promt.replace('[nowDate]', future)
    #print('#########################################', promt)
    try:
        mess = [{'role': 'system', 'content': promt,},
                {'role': 'user', 'content': ' '}]
        answer, allToken, allTokenPrice= gpt.answer(' ',mess,)
        
        row = {'all_price': float(allTokenPrice), 'all_token': int(allToken), 'all_messages': 1}
        print(answer)
        return answer
    except Exception as e:
        print(f'{e=}')

def forecast(day:int):
    answer = forecastText(day)
    words = answer.replace('\n',' ').split(" ")
    # Найти число в строке
    print(words)
    for word in words:
        if word.isdigit():
            number = int(word)
            current_YDB, future_YDB = get_dates_YDB(day)
            row ={
                'time_epoh': time_epoch(),
                'date_open':current_YDB, 
                'date_close':future_YDB,
                'price_close': number }
            sql.insert_query('prognoz', row)
            
            print(number)
            
            return number
            
    print(f'{number=}')  # Вывод: 29536
    
    
def forecastDaily(days:int):
    price = []
    for day in range(1,days+1):
        price.append(forecast(day))
    #current, future = get_dates(day)
    #print("Текущая дата:", current)
    #print(f"Дата через {day} дней:", future)
    print(f'{price=}')
    return {'price': price}

if __name__ == '__main__':
    forecast(1)