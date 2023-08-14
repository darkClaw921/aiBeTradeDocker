from datetime import datetime, timedelta
#import workYDB
import redis
import json
#sql = workYDB.Ydb()
#from workBinance import get_BTC_analit_for

#from chat import GPT
from dotenv import load_dotenv
import os
load_dotenv()
from statistics import mean
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
    current_date = datetime.now().strftime("%d/%m/%Y")

    # Дата, отстоящая на 30 дней
    delta = timedelta(days=day)
    future_date = (datetime.now() + delta).strftime("%d/%m/%Y")

    return current_date, future_date

# Создаем пустой список для хранения нового массива
def array(arr: list)->list:
    new_arr = []
    # Итерируемся по элементам в исходном массиве
    for x in arr:
        # Итерируемся по элементам в каждом вложенном списке
            new_arr.extend(x)
    
    # Выводим новый массив
    return new_arr

def get_average(to:str, lst:list[dict]):
    tempLst = []
    for row in lst:
        tempLst.append(row[to])
    
    average = mean(tempLst)
    return average

if __name__ == '__main__':
    pass