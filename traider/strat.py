
from tradesWork import get_trends
import requests
from pprint import pprint
from loguru import logger
from helper import array, get_average, time_epoch
from workYDB import Ydb
from modelsForecast import get_forecast_SARIMAX

sql = Ydb()


#TODO запрос на получение цены коина это stock /stocks/$stockId/coins/$coin/priceDaily/$from/$to
#получаем прайс на даты как в тренде и потом считаем
#b = [{"date":"2023-08-02","price":"29704.5"},{"date":"2023-08-03","price":"29180.5"},{"date":"2023-08-04","price":"29186"},{"date":"2023-08-05","price":"29088.5"},{"date":"2023-08-06","price":"29053.5"},{"date":"2023-08-07","price":"29064"},{"date":"2023-08-08","price":"29191.5"},{"date":"2023-08-09","price":"29760.5"}]
@logger.catch
def add_7d_trends_to_YDB(onlyNOW=False):
    trends = get_trends()
    first_key = list(trends.keys())[0].split(' ')[0]
    last_key = list(trends.keys())[-1].split(' ')[0]

    #req1 = requests.get(f'http://127.0.0.1:5001/stocks/1/coins/BTCUSD/priceDaily/{first_key}/{last_key}')
    
    req = requests.get(f'http://127.0.0.1:5001/stocks/1/coins/BTCUSD/priceDaily/{first_key}/{last_key}/60')
    
    #req = requests.get(f'{stockURL}/stocks/1/coins/BTCUSD/priceDaily/2023-01-01/2023-08-10/60')
    
    priceNow =requests.get(f'http://127.0.0.1:5001/stocks/1/coins/BTCUSD/price') 
    priceNow = float(eval(priceNow.text)['price'])
    print(f'{priceNow=}')
    
    #print(req.text)stocks/1/coins/BTCUSD/price
    pricePairHour = eval(req.text)
    pricePairHour = array(pricePairHour)
    #print(f'{pricePairHour=}')
    #b=req1.text
    
    #forecast(pricePairHour)
    
    
    #print(pricePairHour)
   
    #pprint(trends)
    i = 0
    RateChange = float(pricePairHour[-2]['price'])-float(pricePairHour[-1]['price'])

    values = list(trends.values())
    last_value = values[-1]
    second_last_value = values[-2]
    BBBU = second_last_value[1] / last_value[0]
    print(f'{RateChange=}')
    print(f'{BBBU=}')

    dateStart = pricePairHour[0]['date'].replace(' ','T')+'Z'
    dateEnd = pricePairHour[-1]['date'].replace(' ','T')+'Z'
    #row = {'date_time': date.replace(' ','T')+'Z',
    #row = {'date_time': pricePairHour[-1]['date'].replace(' ','T')+'Z',
    row = {'date_time': list(trends.keys())[-1].replace(' ','T')+'Z', 
                'bb_bu': BBBU,
               'rate_change': RateChange,
               'strateg': 'strat1'}
    row2 = {
        'time_epoh': time_epoch(),
        'date_close': dateEnd.replace('Z',':00Z'),
        'price_close': float(pricePairHour[-1]['price']),
        'strat': 'real',
        'type': 'real'
    } 
    
    if onlyNOW:
        riskPersent = 0.3
        #sql.replace_query('strateg', row)
        prognoz = get_prognoz(dateStart, dateEnd)
        #sql.replace_query('analitic', row2)
        targetPrice, lowerPrice, upperPrice =get_forecast_SARIMAX(pricePairHour)
        #DealPrice = TargetPrice - RiskPercent ДО ЦЕНЫ TPDownLevel
        riskPrice = (targetPrice - lowerPrice) * riskPersent
        
        print(f'{riskPrice=}')
        priceOpen = targetPrice - riskPrice
        priceClose = targetPrice + riskPrice
        print(f'{priceClose=}')
        print(f'{priceOpen=}')
        #dealPrice = prognozPrice - (lowerPrice + (lowerPrice * riskPersent))
        #dealPrice = targetPrice - riskPrice
        dealPrice = priceOpen 
        print(f'{priceNow=}')
        print(f'{dealPrice=}')
        print(f'{priceNow <= dealPrice=}')
        # row = {
        #     'time_epoh': time_epoch(),
        #     #'date_close': str(dateClose).replace(' ','T')+'Z',
        #     'date_close': dateClose[0],
        #     'price_close': targetPrice,
        #     'strat': 'strat1',
        #     'type': 'prognoz',
        #     'lower_price':lowerPrice,
        #     'upper_price':upperPrice,
        # }
        # sql.replace_query('analitic', row)
        #forecast(pricePairHour)
        #TODO передать параметры для ордера и открыть его 
        
        return prognoz, dealPrice 
        
    # AverageBBBU = []
    # AverageRateChange = []
    #все сразу
    for key,value in trends.items():
        #print(key, b[i]['date'])
        date = key
        BB = value[1] #buy bitcoin
        BU = value[0] #BTC USD
        
        BBBU= BB / BU

        try:
            RateChange = float(pricePairHour[i+1]['price']) - float(pricePairHour[i]['price'])
        except:
            RateChange = float(pricePairHour[i]['price']) - float(pricePairHour[i-1]['price'])
        
        #print(f'{date=} {BBBU=} {RateChange=}') 
        row = {'date_time': date.replace(' ','T')+'Z',
               'bb_bu': BBBU,
               'rate_change': RateChange,
               'strateg': 'strat1'}
        sql.replace_query('strateg', row)
        
        forecast(pricePairHour)
        #sql.insert_query('strateg', row)
        #break
        # Rate = b[i]['price']
        # AverageBBBU.append(BBBU)
        # AverageRateChange.append(Rate)
        i +=1

    prognoz = get_prognoz(dateStart, dateEnd)
    return prognoz


    #pass
def get_prognoz(dateStart,dateEnd):
    #2023-08-02T18:00:00Z
    #add_7d_trends_to_YDB()
    dateStart= dateStart.replace('Z',':00Z')
    dateEnd= dateEnd.replace('Z',':00Z')
    data =sql.select_query('strateg', f'datetime("{dateEnd}") > date_time and datetime("{dateStart}") < date_time ')
    BBBU = data[-1]["bb_bu"]
    RateChange= data[-1]['rate_change']
    #pprint(a)
    AverageBBBU = get_average(to='bb_bu',lst=data)
    print(f'{AverageBBBU=}')
    print(f'{BBBU=}')

    AverageRateChange = get_average(to='rate_change',lst=data)
    print(f'{AverageRateChange=}')
    print(f'{RateChange=}')

    if BBBU > AverageBBBU and RateChange > AverageRateChange:
        return 'BUY'
    else: return 'SELL' 

#def forecast(data):
def forecastARIMA(data):
    import pandas as pd
    from statsmodels.tsa.arima.model import ARIMA

    # Преобразуем данные в pandas DataFrame
    # data = [{'date': '2023-08-10 01:08', 'price': '29519'},
    #         {'date': '2023-08-10 02:08', 'price': '29594'},
    #         {'date': '2023-08-10 03:08', 'price': '29572'},
    #         {'date': '2023-08-10 04:08', 'price': '29613.5'},
    #         {'date': '2023-08-10 05:08', 'price': '29610.5'},
    #         {'date': '2023-08-10 06:08', 'price': '29577.5'},
    #         {'date': '2023-08-10 07:08', 'price': '29573.5'},
    #         {'date': '2023-08-10 08:08', 'price': '29527.5'},
    #         {'date': '2023-08-10 09:08', 'price': '29573.5'},
    #         {'date': '2023-08-10 10:08', 'price': '29500'},
    #         {'date': '2023-08-10 11:08', 'price': '29496'}]

    df = pd.DataFrame(data)

    # Преобразуем столбец с датами в формат datetime
    df['date'] = pd.to_datetime(df['date'])

    # Установим столбец с датами в качестве индекса
    df.set_index('date', inplace=True)

    # Преобразуем значения столбца 'price' в числа с плавающей точкой
    df['price'] = df['price'].astype(float)

    # Создаем модель ARIMA
    model = ARIMA(df['price'], order=(1, 0, 0))

    # Обучаем модель на исходных данных
    model_fit = model.fit()

    # Прогнозируем будущие значения
    forecast = model_fit.forecast(steps=1)

    print(f'{forecast=}')
    dateClose = forecast.keys()[0]
    priceClose = forecast[0] 
    #b = forecast[0]
    #print(a,b)
    # forecast_values = forecast.predicted_mean()
    # lower_bound = forecast.conf_int()["lower price"]
    # upper_bound = forecast.conf_int()["upper price"]

    # print(forecast_values)
    # print(lower_bound)
    # print(upper_bound)
    # 1/0
    for key, value in forecast.items():
        dateClose = key 
        priceClose = value
        # row = {
        #     'time_epoh': time_epoch(),
        #     'date_close': str(dateClose).replace(' ','T')+'Z',
        #     'price_close': priceClose,
        #     'strat': 'strat1',
        #     'type': 'prognoz'
        # }
        row = {
            'time_epoh': time_epoch(),
            'date_close': str(dateClose).replace(' ','T')+'Z',
            'price_close': priceClose,
            'strat': 'strat1',
            'type': 'prognoz'
        } 
        #sql.replace_query('analitic', row)
        sql.replace_query('analitic', row)

@logger.catch
def forecast(data):
    import pandas as pd
    import statsmodels.api as sm

    # Преобразование данных во временной ряд
    # data = [{'date': '2023-08-10 01:08', 'price': '29519'}, {'date': '2023-08-10 02:08', 'price': '29594'},
    #         {'date': '2023-08-10 03:08', 'price': '29572'}, {'date': '2023-08-10 04:08', 'price': '29613.5'},
    #         {'date': '2023-08-10 05:08', 'price': '29610.5'}, {'date': '2023-08-10 06:08', 'price': '29577.5'},
    #         {'date': '2023-08-10 07:08', 'price': '29573.5'}, {'date': '2023-08-10 08:08', 'price': '29527.5'},
    #         {'date': '2023-08-10 09:08', 'price': '29573.5'}, {'date': '2023-08-10 10:08', 'price': '29500'},
    #         {'date': '2023-08-10 11:08', 'price': '29496'}]
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['price'] = pd.to_numeric(df['price'])
    df.set_index('date', inplace=True)

    # Обучение модели ARIMA
    model = sm.tsa.ARIMA(df['price'], order=(1, 0, 0))
    results = model.fit()

    # Прогнозирование значений
    forecast = results.get_forecast(steps=1)

    # Извлечение прогнозных значений и доверительных интервалов
    # f1orecast_values = forecast.predicted_mean
    # print(f1orecast_values)
    #forecast_values = forecast.conf_int()
    # print(f'{forecast_values=}')
    # for i in forecast:
    #     print(i)
    # 1/0
    b = forecast.row_labels[0]
    print(b)
    lower_bound = forecast.conf_int()["lower price"]
    upper_bound = forecast.conf_int()["upper price"]

    # print(f'{forecast_values=}')
    print(f'{lower_bound=}')
    print(f'{upper_bound=}')
    print(len(forecast.conf_int()))
    print(f'{forecast.conf_int()=}')
    print(f'{forecast.predicted_mean=}')
    #for key, value in forecast.items():
    for i,date in enumerate(forecast.row_labels):
    #for key,value in forecast.conf_int().items():
        dateClose = str(date).replace(' ','T')+'Z',
        forecast_values = forecast.predicted_mean[i]
        priceClose = forecast_values
        
        lower_bound = forecast.conf_int()["lower price"][i]
        upper_bound = forecast.conf_int()["upper price"][i]

        row = {
            'time_epoh': time_epoch(),
            #'date_close': str(dateClose).replace(' ','T')+'Z',
            'date_close': dateClose[0],
            'price_close': priceClose,
            'strat': 'strat1',
            'type': 'prognoz',
            'lower_price':lower_bound,
            'upper_price':upper_bound,
        } 
        #sql.replace_query('analitic', row)
        sql.replace_query('analitic', row)
        





def main():
    #pr = get_prognoz('2023-08-02', '2023-08-04')
    pr = add_7d_trends_to_YDB(onlyNOW=True)
    print(f'{pr=}')

def add_real_price(data):
    for i in data:
        row = {
                'time_epoh': time_epoch(),
                'date_close': str(i['date']).replace(' ','T')+':00Z',
                'price_close': i['price'],
                'strat': 'real',
                'type': 'real'
            } 
            #sql.replace_query('analitic', row)
        sql.replace_query('analitic', row)

def get_only_price(data):
    prices = []
    dates = []
    for date,i in enumerate(data):
        prices.append(float(i['price']))
        dates.append(date)
    return dates

def prepare_data_excel(data):
    import pandas as pd
    b=[]
    for i in data:
        d = i['date'].split(' ')[0].split('-')
        d = f'{d[2]}.{d[1]}.{d[0]}'
        p = float(i['price'])

        b.append({'data': d, 'price': p})
    df = pd.DataFrame(b)

    # Сохраняем DataFrame в файл Excel
    df.to_excel('data1.xlsx', index=False)   

if __name__ == "__main__":
    #b = [{'date': '2023-08-03 00:08', 'price': '29128'}, {'date': '2023-08-03 01:08', 'price': '29182.5'}, {'date': '2023-08-03 02:08', 'price': '29179.5'}, {'date': '2023-08-03 03:08', 'price': '29180.5'}, {'date': '2023-08-03 04:08', 'price': '29158.5'}, {'date': '2023-08-03 05:08', 'price': '29239'}, {'date': '2023-08-03 06:08', 'price': '29168'}, {'date': '2023-08-03 07:08', 'price': '29164'}, {'date': '2023-08-03 08:08', 'price': '29114.5'}, {'date': '2023-08-03 09:08', 'price': '29132.5'}, {'date': '2023-08-03 10:08', 'price': '29067.5'}, {'date': '2023-08-03 11:08', 'price': '29020'}, {'date': '2023-08-03 12:08', 'price': '29105.5'}, {'date': '2023-08-03 13:08', 'price': '29144.5'}, {'date': '2023-08-03 14:08', 'price': '29165'}, {'date': '2023-08-03 15:08', 'price': '29132.5'}, {'date': '2023-08-03 16:08', 'price': '29095.5'}, {'date': '2023-08-03 17:08', 'price': '29179'}, {'date': '2023-08-03 18:08', 'price': '29394'}, {'date': '2023-08-03 19:08', 'price': '29247'}, {'date': '2023-08-03 20:08', 'price': '29298.5'}, {'date': '2023-08-03 21:08', 'price': '29232'}, {'date': '2023-08-03 22:08', 'price': '29278'}, {'date': '2023-08-03 23:08', 'price': '29279'}, {'date': '2023-08-04 00:08', 'price': '29296'}, {'date': '2023-08-04 01:08', 'price': '29243'}, {'date': '2023-08-04 02:08', 'price': '29235.5'}, {'date': '2023-08-04 03:08', 'price': '29186'}, {'date': '2023-08-04 04:08', 'price': '29233'}, {'date': '2023-08-04 05:08', 'price': '29202'}, {'date': '2023-08-04 06:08', 'price': '29164'}, {'date': '2023-08-04 07:08', 'price': '29158'}, {'date': '2023-08-04 08:08', 'price': '29201'}, {'date': '2023-08-04 09:08', 'price': '29235'}, {'date': '2023-08-04 10:08', 'price': '29186.5'}, {'date': '2023-08-04 11:08', 'price': '29206.5'}, {'date': '2023-08-04 12:08', 'price': '29176'}, {'date': '2023-08-04 13:08', 'price': '29189.5'}, {'date': '2023-08-04 14:08', 'price': '29154'}, {'date': '2023-08-04 15:08', 'price': '29160.5'}, {'date': '2023-08-04 16:08', 'price': '29205'}, {'date': '2023-08-04 17:08', 'price': '29223.5'}, {'date': '2023-08-04 18:08', 'price': '29242.5'}, {'date': '2023-08-04 19:08', 'price': '29254.5'}, {'date': '2023-08-04 20:08', 'price': '29250'}, {'date': '2023-08-04 21:08', 'price': '29188.5'}, {'date': '2023-08-04 22:08', 'price': '29047.5'}, {'date': '2023-08-04 23:08', 'price': '29009'}, {'date': '2023-08-05 00:08', 'price': '28942'}, {'date': '2023-08-05 01:08', 'price': '29032'}, {'date': '2023-08-05 02:08', 'price': '29027.5'}, {'date': '2023-08-05 03:08', 'price': '29088.5'}, {'date': '2023-08-05 04:08', 'price': '29090'}, {'date': '2023-08-05 05:08', 'price': '29041'}, {'date': '2023-08-05 06:08', 'price': '29058.5'}, {'date': '2023-08-05 07:08', 'price': '29054.5'}, {'date': '2023-08-05 08:08', 'price': '29014'}, {'date': '2023-08-05 09:08', 'price': '29063'}, {'date': '2023-08-05 10:08', 'price': '29031'}, {'date': '2023-08-05 11:08', 'price': '29020'}, {'date': '2023-08-05 12:08', 'price': '29060'}, {'date': '2023-08-05 13:08', 'price': '29035.5'}, {'date': '2023-08-05 14:08', 'price': '29032.5'}, {'date': '2023-08-05 15:08', 'price': '29024'}, {'date': '2023-08-05 16:08', 'price': '28998'}, {'date': '2023-08-05 17:08', 'price': '29013.5'}, {'date': '2023-08-05 18:08', 'price': '29054'}, {'date': '2023-08-05 19:08', 'price': '29018'}, {'date': '2023-08-05 20:08', 'price': '29013'}, {'date': '2023-08-05 21:08', 'price': '29037.5'}, {'date': '2023-08-05 22:08', 'price': '29050'}, {'date': '2023-08-05 23:08', 'price': '29044'}, {'date': '2023-08-06 00:08', 'price': '29038'}, {'date': '2023-08-06 01:08', 'price': '29055.5'}, {'date': '2023-08-06 02:08', 'price': '29069.5'}, {'date': '2023-08-06 03:08', 'price': '29053.5'}, {'date': '2023-08-06 04:08', 'price': '29044.5'}, {'date': '2023-08-06 05:08', 'price': '29020'}, {'date': '2023-08-06 06:08', 'price': '29047'}, {'date': '2023-08-06 07:08', 'price': '29039.5'}, {'date': '2023-08-06 08:08', 'price': '29055'}, {'date': '2023-08-06 09:08', 'price': '29081.5'}, {'date': '2023-08-06 10:08', 'price': '29047'}, {'date': '2023-08-06 11:08', 'price': '29073.5'}, {'date': '2023-08-06 12:08', 'price': '29094'}, {'date': '2023-08-06 13:08', 'price': '29059'}, {'date': '2023-08-06 14:08', 'price': '29049'}, {'date': '2023-08-06 15:08', 'price': '29054'}, {'date': '2023-08-06 16:08', 'price': '29014.5'}, {'date': '2023-08-06 17:08', 'price': '29000'}, {'date': '2023-08-06 18:08', 'price': '29023'}, {'date': '2023-08-06 19:08', 'price': '28991'}, {'date': '2023-08-06 20:08', 'price': '29064.5'}, {'date': '2023-08-06 21:08', 'price': '29073.5'}, {'date': '2023-08-06 22:08', 'price': '29074'}, {'date': '2023-08-06 23:08', 'price': '29070'}, {'date': '2023-08-07 00:08', 'price': '29114'}, {'date': '2023-08-07 01:08', 'price': '29061.5'}, {'date': '2023-08-07 02:08', 'price': '29078.5'}, {'date': '2023-08-07 03:08', 'price': '29064'}, {'date': '2023-08-07 04:08', 'price': '29025.5'}, {'date': '2023-08-07 05:08', 'price': '29117'}, {'date': '2023-08-07 06:08', 'price': '29173.5'}, {'date': '2023-08-07 07:08', 'price': '29129.5'}, {'date': '2023-08-07 08:08', 'price': '29156.5'}, {'date': '2023-08-07 09:08', 'price': '29090'}, {'date': '2023-08-07 10:08', 'price': '29015'}, {'date': '2023-08-07 11:08', 'price': '29058.5'}, {'date': '2023-08-07 12:08', 'price': '29029.5'}, {'date': '2023-08-07 13:08', 'price': '29052'}, {'date': '2023-08-07 14:08', 'price': '29102'}, {'date': '2023-08-07 15:08', 'price': '29044'}, {'date': '2023-08-07 16:08', 'price': '29028'}, {'date': '2023-08-07 17:08', 'price': '29001.5'}, {'date': '2023-08-07 18:08', 'price': '28998'}, {'date': '2023-08-07 19:08', 'price': '28839'}, {'date': '2023-08-07 20:08', 'price': '28922'}, {'date': '2023-08-07 21:08', 'price': '28953.5'}, {'date': '2023-08-07 22:08', 'price': '29078'}, {'date': '2023-08-07 23:08', 'price': '29142.5'}, {'date': '2023-08-08 00:08', 'price': '29183'}, {'date': '2023-08-08 01:08', 'price': '29175.5'}, {'date': '2023-08-08 02:08', 'price': '29157'}, {'date': '2023-08-08 03:08', 'price': '29191.5'}, {'date': '2023-08-08 04:08', 'price': '29235'}, {'date': '2023-08-08 05:08', 'price': '29125.5'}, {'date': '2023-08-08 06:08', 'price': '29152.5'}, {'date': '2023-08-08 07:08', 'price': '29178'}, {'date': '2023-08-08 08:08', 'price': '29206'}, {'date': '2023-08-08 09:08', 'price': '29235'}, {'date': '2023-08-08 10:08', 'price': '29204'}, {'date': '2023-08-08 11:08', 'price': '29168'}, {'date': '2023-08-08 12:08', 'price': '29160.5'}, {'date': '2023-08-08 13:08', 'price': '29182.5'}, {'date': '2023-08-08 14:08', 'price': '29280'}, {'date': '2023-08-08 15:08', 'price': '29414'}, {'date': '2023-08-08 16:08', 'price': '29567'}, {'date': '2023-08-08 17:08', 'price': '29333'}, {'date': '2023-08-08 18:08', 'price': '29421.5'}, {'date': '2023-08-08 19:08', 'price': '29516.5'}, {'date': '2023-08-08 20:08', 'price': '29730'}, {'date': '2023-08-08 21:08', 'price': '29788'}, {'date': '2023-08-08 22:08', 'price': '29830'}, {'date': '2023-08-08 23:08', 'price': '29864'}, {'date': '2023-08-09 00:08', 'price': '29970.5'}, {'date': '2023-08-09 01:08', 'price': '29851.5'}, {'date': '2023-08-09 02:08', 'price': '29761'}, {'date': '2023-08-09 03:08', 'price': '29760.5'}, {'date': '2023-08-09 04:08', 'price': '29770.5'}, {'date': '2023-08-09 05:08', 'price': '29843'}, {'date': '2023-08-09 06:08', 'price': '29686'}, {'date': '2023-08-09 07:08', 'price': '29699.5'}, {'date': '2023-08-09 08:08', 'price': '29746.5'}, {'date': '2023-08-09 09:08', 'price': '29718.5'}, {'date': '2023-08-09 10:08', 'price': '29712.5'}, {'date': '2023-08-09 11:08', 'price': '29811'}, {'date': '2023-08-09 12:08', 'price': '29827'}, {'date': '2023-08-09 13:08', 'price': '29770'}, {'date': '2023-08-09 14:08', 'price': '29835'}, {'date': '2023-08-09 15:08', 'price': '29886'}, {'date': '2023-08-09 16:08', 'price': '30064.5'}, {'date': '2023-08-09 17:08', 'price': '29872'}, {'date': '2023-08-09 18:08', 'price': '29751'}, {'date': '2023-08-09 19:08', 'price': '29746.5'}, {'date': '2023-08-09 20:08', 'price': '29495.5'}, {'date': '2023-08-09 21:08', 'price': '29500'}, {'date': '2023-08-09 22:08', 'price': '29510'}, {'date': '2023-08-09 23:08', 'price': '29395.5'}, {'date': '2023-08-10 00:08', 'price': '29495'}, {'date': '2023-08-10 01:08', 'price': '29519'}, {'date': '2023-08-10 02:08', 'price': '29594'}, {'date': '2023-08-10 03:08', 'price': '29572'}, {'date': '2023-08-10 04:08', 'price': '29613.5'}, {'date': '2023-08-10 05:08', 'price': '29610.5'}, {'date': '2023-08-10 06:08', 'price': '29577.5'}, {'date': '2023-08-10 07:08', 'price': '29573.5'}, {'date': '2023-08-10 08:08', 'price': '29527.5'}, {'date': '2023-08-10 09:08', 'price': '29573.5'}, {'date': '2023-08-10 10:08', 'price': '29500'}, {'date': '2023-08-10 11:08', 'price': '29496'}]
    #b1 =[{'date': '2023-08-03 00:08', 'price': '29128'}, {'date': '2023-08-03 01:08', 'price': '29182.5'}, {'date': '2023-08-03 02:08', 'price': '29179.5'}, {'date': '2023-08-03 03:08', 'price': '29180.5'}, {'date': '2023-08-03 04:08', 'price': '29158.5'}, {'date': '2023-08-03 05:08', 'price': '29239'}, {'date': '2023-08-03 06:08', 'price': '29168'}, {'date': '2023-08-03 07:08', 'price': '29164'}, {'date': '2023-08-03 08:08', 'price': '29114.5'}, {'date': '2023-08-03 09:08', 'price': '29132.5'}, {'date': '2023-08-03 10:08', 'price': '29067.5'}, {'date': '2023-08-03 11:08', 'price': '29020'}, {'date': '2023-08-03 12:08', 'price': '29105.5'}, {'date': '2023-08-03 13:08', 'price': '29144.5'}, {'date': '2023-08-03 14:08', 'price': '29165'}, {'date': '2023-08-03 15:08', 'price': '29132.5'}, {'date': '2023-08-03 16:08', 'price': '29095.5'}, {'date': '2023-08-03 17:08', 'price': '29179'}, {'date': '2023-08-03 18:08', 'price': '29394'}, {'date': '2023-08-03 19:08', 'price': '29247'}, {'date': '2023-08-03 20:08', 'price': '29298.5'}, {'date': '2023-08-03 21:08', 'price': '29232'}, {'date': '2023-08-03 22:08', 'price': '29278'}, {'date': '2023-08-03 23:08', 'price': '29279'}, {'date': '2023-08-04 00:08', 'price': '29296'}, {'date': '2023-08-04 01:08', 'price': '29243'}, {'date': '2023-08-04 02:08', 'price': '29235.5'}, {'date': '2023-08-04 03:08', 'price': '29186'}, {'date': '2023-08-04 04:08', 'price': '29233'}, {'date': '2023-08-04 05:08', 'price': '29202'}, {'date': '2023-08-04 06:08', 'price': '29164'}, {'date': '2023-08-04 07:08', 'price': '29158'}, {'date': '2023-08-04 08:08', 'price': '29201'}, {'date': '2023-08-04 09:08', 'price': '29235'}, {'date': '2023-08-04 10:08', 'price': '29186.5'}, {'date': '2023-08-04 11:08', 'price': '29206.5'}, {'date': '2023-08-04 12:08', 'price': '29176'}, {'date': '2023-08-04 13:08', 'price': '29189.5'}, {'date': '2023-08-04 14:08', 'price': '29154'}, {'date': '2023-08-04 15:08', 'price': '29160.5'}, {'date': '2023-08-04 16:08', 'price': '29205'}, {'date': '2023-08-04 17:08', 'price': '29223.5'}, {'date': '2023-08-04 18:08', 'price': '29242.5'}, {'date': '2023-08-04 19:08', 'price': '29254.5'}, {'date': '2023-08-04 20:08', 'price': '29250'}, {'date': '2023-08-04 21:08', 'price': '29188.5'}, {'date': '2023-08-04 22:08', 'price': '29047.5'}, {'date': '2023-08-04 23:08', 'price': '29009'}, {'date': '2023-08-05 00:08', 'price': '28942'}, {'date': '2023-08-05 01:08', 'price': '29032'}, {'date': '2023-08-05 02:08', 'price': '29027.5'}, {'date': '2023-08-05 03:08', 'price': '29088.5'}, {'date': '2023-08-05 04:08', 'price': '29090'}, {'date': '2023-08-05 05:08', 'price': '29041'}, {'date': '2023-08-05 06:08', 'price': '29058.5'}, {'date': '2023-08-05 07:08', 'price': '29054.5'}, {'date': '2023-08-05 08:08', 'price': '29014'}, {'date': '2023-08-05 09:08', 'price': '29063'}, {'date': '2023-08-05 10:08', 'price': '29031'}, {'date': '2023-08-05 11:08', 'price': '29020'}, {'date': '2023-08-05 12:08', 'price': '29060'}, {'date': '2023-08-05 13:08', 'price': '29035.5'}, {'date': '2023-08-05 14:08', 'price': '29032.5'}, {'date': '2023-08-05 15:08', 'price': '29024'}, {'date': '2023-08-05 16:08', 'price': '28998'}, {'date': '2023-08-05 17:08', 'price': '29013.5'}, {'date': '2023-08-05 18:08', 'price': '29054'}, {'date': '2023-08-05 19:08', 'price': '29018'}, {'date': '2023-08-05 20:08', 'price': '29013'}, {'date': '2023-08-05 21:08', 'price': '29037.5'}, {'date': '2023-08-05 22:08', 'price': '29050'}, {'date': '2023-08-05 23:08', 'price': '29044'}, {'date': '2023-08-06 00:08', 'price': '29038'}, {'date': '2023-08-06 01:08', 'price': '29055.5'}, {'date': '2023-08-06 02:08', 'price': '29069.5'}, {'date': '2023-08-06 03:08', 'price': '29053.5'}, {'date': '2023-08-06 04:08', 'price': '29044.5'}, {'date': '2023-08-06 05:08', 'price': '29020'}, {'date': '2023-08-06 06:08', 'price': '29047'}, {'date': '2023-08-06 07:08', 'price': '29039.5'}, {'date': '2023-08-06 08:08', 'price': '29055'}, {'date': '2023-08-06 09:08', 'price': '29081.5'}, {'date': '2023-08-06 10:08', 'price': '29047'}, {'date': '2023-08-06 11:08', 'price': '29073.5'}, {'date': '2023-08-06 12:08', 'price': '29094'}, {'date': '2023-08-06 13:08', 'price': '29059'}, {'date': '2023-08-06 14:08', 'price': '29049'}, {'date': '2023-08-06 15:08', 'price': '29054'}, {'date': '2023-08-06 16:08', 'price': '29014.5'}, {'date': '2023-08-06 17:08', 'price': '29000'}, {'date': '2023-08-06 18:08', 'price': '29023'}, {'date': '2023-08-06 19:08', 'price': '28991'}, {'date': '2023-08-06 20:08', 'price': '29064.5'}, {'date': '2023-08-06 21:08', 'price': '29073.5'}, {'date': '2023-08-06 22:08', 'price': '29074'}, {'date': '2023-08-06 23:08', 'price': '29070'}, {'date': '2023-08-07 00:08', 'price': '29114'}, {'date': '2023-08-07 01:08', 'price': '29061.5'}, {'date': '2023-08-07 02:08', 'price': '29078.5'}, {'date': '2023-08-07 03:08', 'price': '29064'}, {'date': '2023-08-07 04:08', 'price': '29025.5'}, {'date': '2023-08-07 05:08', 'price': '29117'}, {'date': '2023-08-07 06:08', 'price': '29173.5'}, {'date': '2023-08-07 07:08', 'price': '29129.5'}, {'date': '2023-08-07 08:08', 'price': '29156.5'}, {'date': '2023-08-07 09:08', 'price': '29090'}, {'date': '2023-08-07 10:08', 'price': '29015'}, {'date': '2023-08-07 11:08', 'price': '29058.5'}, {'date': '2023-08-07 12:08', 'price': '29029.5'}, {'date': '2023-08-07 13:08', 'price': '29052'}, {'date': '2023-08-07 14:08', 'price': '29102'}, {'date': '2023-08-07 15:08', 'price': '29044'}, {'date': '2023-08-07 16:08', 'price': '29028'}, {'date': '2023-08-07 17:08', 'price': '29001.5'}, {'date': '2023-08-07 18:08', 'price': '28998'}, {'date': '2023-08-07 19:08', 'price': '28839'}, {'date': '2023-08-07 20:08', 'price': '28922'}, {'date': '2023-08-07 21:08', 'price': '28953.5'}, {'date': '2023-08-07 22:08', 'price': '29078'}, {'date': '2023-08-07 23:08', 'price': '29142.5'}, {'date': '2023-08-08 00:08', 'price': '29183'}, {'date': '2023-08-08 01:08', 'price': '29175.5'}, {'date': '2023-08-08 02:08', 'price': '29157'}, {'date': '2023-08-08 03:08', 'price': '29191.5'}, {'date': '2023-08-08 04:08', 'price': '29235'}, {'date': '2023-08-08 05:08', 'price': '29125.5'}, {'date': '2023-08-08 06:08', 'price': '29152.5'}, {'date': '2023-08-08 07:08', 'price': '29178'}, {'date': '2023-08-08 08:08', 'price': '29206'}, {'date': '2023-08-08 09:08', 'price': '29235'}, {'date': '2023-08-08 10:08', 'price': '29204'}, {'date': '2023-08-08 11:08', 'price': '29168'}, {'date': '2023-08-08 12:08', 'price': '29160.5'}, {'date': '2023-08-08 13:08', 'price': '29182.5'}, {'date': '2023-08-08 14:08', 'price': '29280'}, {'date': '2023-08-08 15:08', 'price': '29414'}, {'date': '2023-08-08 16:08', 'price': '29567'}, {'date': '2023-08-08 17:08', 'price': '29333'}, {'date': '2023-08-08 18:08', 'price': '29421.5'}, {'date': '2023-08-08 19:08', 'price': '29516.5'}, {'date': '2023-08-08 20:08', 'price': '29730'}, {'date': '2023-08-08 21:08', 'price': '29788'}, {'date': '2023-08-08 22:08', 'price': '29830'}, {'date': '2023-08-08 23:08', 'price': '29864'}, {'date': '2023-08-09 00:08', 'price': '29970.5'}, {'date': '2023-08-09 01:08', 'price': '29851.5'}, {'date': '2023-08-09 02:08', 'price': '29761'}, {'date': '2023-08-09 03:08', 'price': '29760.5'}, {'date': '2023-08-09 04:08', 'price': '29770.5'}, {'date': '2023-08-09 05:08', 'price': '29843'}, {'date': '2023-08-09 06:08', 'price': '29686'}, {'date': '2023-08-09 07:08', 'price': '29699.5'}, {'date': '2023-08-09 08:08', 'price': '29746.5'}, {'date': '2023-08-09 09:08', 'price': '29718.5'}, {'date': '2023-08-09 10:08', 'price': '29712.5'}, {'date': '2023-08-09 11:08', 'price': '29811'}, {'date': '2023-08-09 12:08', 'price': '29827'}, {'date': '2023-08-09 13:08', 'price': '29770'}, {'date': '2023-08-09 14:08', 'price': '29835'}, {'date': '2023-08-09 15:08', 'price': '29886'}, {'date': '2023-08-09 16:08', 'price': '30064.5'}, {'date': '2023-08-09 17:08', 'price': '29872'}, {'date': '2023-08-09 18:08', 'price': '29751'}, {'date': '2023-08-09 19:08', 'price': '29746.5'}, {'date': '2023-08-09 20:08', 'price': '29495.5'}, {'date': '2023-08-09 21:08', 'price': '29500'}, {'date': '2023-08-09 22:08', 'price': '29510'}, {'date': '2023-08-09 23:08', 'price': '29395.5'}, {'date': '2023-08-10 00:08', 'price': '29495'}, {'date': '2023-08-10 01:08', 'price': '29519'}, {'date': '2023-08-10 02:08', 'price': '29594'}, {'date': '2023-08-10 03:08', 'price': '29572'}, {'date': '2023-08-10 04:08', 'price': '29613.5'}, {'date': '2023-08-10 05:08', 'price': '29610.5'}, {'date': '2023-08-10 06:08', 'price': '29577.5'}, {'date': '2023-08-10 07:08', 'price': '29573.5'}, {'date': '2023-08-10 08:08', 'price': '29527.5'}, {'date': '2023-08-10 09:08', 'price': '29573.5'}, {'date': '2023-08-10 10:08', 'price': '29500'}, {'date': '2023-08-10 11:08', 'price': '29496'}, {'date': '2023-08-10 12:08', 'price': '29501'}, {'date': '2023-08-10 13:08', 'price': '29523'}, {'date': '2023-08-10 14:08', 'price': '29541'}, {'date': '2023-08-10 15:08', 'price': '29490.5'}, {'date': '2023-08-10 16:08', 'price': '29544.5'}, {'date': '2023-08-10 17:08', 'price': '29667'}, {'date': '2023-08-10 18:08', 'price': '29476'}]    
    #b = [{'date': '2023-08-02 13:08', 'price': '29452'}, {'date': '2023-08-02 14:08', 'price': '29533.5'}, {'date': '2023-08-02 15:08', 'price': '29560'}, {'date': '2023-08-02 16:08', 'price': '29454'}, {'date': '2023-08-02 17:08', 'price': '29402.5'}, {'date': '2023-08-02 18:08', 'price': '29264.5'}, {'date': '2023-08-02 19:08', 'price': '29324'}, {'date': '2023-08-02 20:08', 'price': '29024'}, {'date': '2023-08-02 21:08', 'price': '29132.5'}, {'date': '2023-08-02 22:08', 'price': '29139.5'}, {'date': '2023-08-02 23:08', 'price': '29150'}, {'date': '2023-08-03 00:08', 'price': '29128'}, {'date': '2023-08-03 01:08', 'price': '29182.5'}, {'date': '2023-08-03 02:08', 'price': '29179.5'}, {'date': '2023-08-03 03:08', 'price': '29180.5'}, {'date': '2023-08-03 04:08', 'price': '29158.5'}, {'date': '2023-08-03 05:08', 'price': '29239'}, {'date': '2023-08-03 06:08', 'price': '29168'}, {'date': '2023-08-03 07:08', 'price': '29164'}, {'date': '2023-08-03 08:08', 'price': '29114.5'}, {'date': '2023-08-03 09:08', 'price': '29132.5'}, {'date': '2023-08-03 10:08', 'price': '29067.5'}, {'date': '2023-08-03 11:08', 'price': '29020'}, {'date': '2023-08-03 12:08', 'price': '29105.5'}, {'date': '2023-08-03 13:08', 'price': '29144.5'}, {'date': '2023-08-03 14:08', 'price': '29165'}, {'date': '2023-08-03 15:08', 'price': '29132.5'}, {'date': '2023-08-03 16:08', 'price': '29095.5'}, {'date': '2023-08-03 17:08', 'price': '29179'}, {'date': '2023-08-03 18:08', 'price': '29394'}, {'date': '2023-08-03 19:08', 'price': '29247'}, {'date': '2023-08-03 20:08', 'price': '29298.5'}, {'date': '2023-08-03 21:08', 'price': '29232'}, {'date': '2023-08-03 22:08', 'price': '29278'}, {'date': '2023-08-03 23:08', 'price': '29279'}, {'date': '2023-08-04 00:08', 'price': '29296'}, {'date': '2023-08-04 01:08', 'price': '29243'}, {'date': '2023-08-04 02:08', 'price': '29235.5'}, {'date': '2023-08-04 03:08', 'price': '29186'}, {'date': '2023-08-04 04:08', 'price': '29233'}, {'date': '2023-08-04 05:08', 'price': '29202'}, {'date': '2023-08-04 06:08', 'price': '29164'}, {'date': '2023-08-04 07:08', 'price': '29158'}, {'date': '2023-08-04 08:08', 'price': '29201'}, {'date': '2023-08-04 09:08', 'price': '29235'}, {'date': '2023-08-04 10:08', 'price': '29186.5'}, {'date': '2023-08-04 11:08', 'price': '29206.5'}, {'date': '2023-08-04 12:08', 'price': '29176'}, {'date': '2023-08-04 13:08', 'price': '29189.5'}, {'date': '2023-08-04 14:08', 'price': '29154'}, {'date': '2023-08-04 15:08', 'price': '29160.5'}, {'date': '2023-08-04 16:08', 'price': '29205'}, {'date': '2023-08-04 17:08', 'price': '29223.5'}, {'date': '2023-08-04 18:08', 'price': '29242.5'}, {'date': '2023-08-04 19:08', 'price': '29254.5'}, {'date': '2023-08-04 20:08', 'price': '29250'}, {'date': '2023-08-04 21:08', 'price': '29188.5'}, {'date': '2023-08-04 22:08', 'price': '29047.5'}, {'date': '2023-08-04 23:08', 'price': '29009'}, {'date': '2023-08-05 00:08', 'price': '28942'}, {'date': '2023-08-05 01:08', 'price': '29032'}, {'date': '2023-08-05 02:08', 'price': '29027.5'}, {'date': '2023-08-05 03:08', 'price': '29088.5'}, {'date': '2023-08-05 04:08', 'price': '29090'}, {'date': '2023-08-05 05:08', 'price': '29041'}, {'date': '2023-08-05 06:08', 'price': '29058.5'}, {'date': '2023-08-05 07:08', 'price': '29054.5'}, {'date': '2023-08-05 08:08', 'price': '29014'}, {'date': '2023-08-05 09:08', 'price': '29063'}, {'date': '2023-08-05 10:08', 'price': '29031'}, {'date': '2023-08-05 11:08', 'price': '29020'}, {'date': '2023-08-05 12:08', 'price': '29060'}, {'date': '2023-08-05 13:08', 'price': '29035.5'}, {'date': '2023-08-05 14:08', 'price': '29032.5'}, {'date': '2023-08-05 15:08', 'price': '29024'}, {'date': '2023-08-05 16:08', 'price': '28998'}, {'date': '2023-08-05 17:08', 'price': '29013.5'}, {'date': '2023-08-05 18:08', 'price': '29054'}, {'date': '2023-08-05 19:08', 'price': '29018'}, {'date': '2023-08-05 20:08', 'price': '29013'}, {'date': '2023-08-05 21:08', 'price': '29037.5'}, {'date': '2023-08-05 22:08', 'price': '29050'}, {'date': '2023-08-05 23:08', 'price': '29044'}, {'date': '2023-08-06 00:08', 'price': '29038'}, {'date': '2023-08-06 01:08', 'price': '29055.5'}, {'date': '2023-08-06 02:08', 'price': '29069.5'}, {'date': '2023-08-06 03:08', 'price': '29053.5'}, {'date': '2023-08-06 04:08', 'price': '29044.5'}, {'date': '2023-08-06 05:08', 'price': '29020'}, {'date': '2023-08-06 06:08', 'price': '29047'}, {'date': '2023-08-06 07:08', 'price': '29039.5'}, {'date': '2023-08-06 08:08', 'price': '29055'}, {'date': '2023-08-06 09:08', 'price': '29081.5'}, {'date': '2023-08-06 10:08', 'price': '29047'}, {'date': '2023-08-06 11:08', 'price': '29073.5'}, {'date': '2023-08-06 12:08', 'price': '29094'}, {'date': '2023-08-06 13:08', 'price': '29059'}, {'date': '2023-08-06 14:08', 'price': '29049'}, {'date': '2023-08-06 15:08', 'price': '29054'}, {'date': '2023-08-06 16:08', 'price': '29014.5'}, {'date': '2023-08-06 17:08', 'price': '29000'}, {'date': '2023-08-06 18:08', 'price': '29023'}, {'date': '2023-08-06 19:08', 'price': '28991'}, {'date': '2023-08-06 20:08', 'price': '29064.5'}, {'date': '2023-08-06 21:08', 'price': '29073.5'}, {'date': '2023-08-06 22:08', 'price': '29074'}, {'date': '2023-08-06 23:08', 'price': '29070'}, {'date': '2023-08-07 00:08', 'price': '29114'}, {'date': '2023-08-07 01:08', 'price': '29061.5'}, {'date': '2023-08-07 02:08', 'price': '29078.5'}, {'date': '2023-08-07 03:08', 'price': '29064'}, {'date': '2023-08-07 04:08', 'price': '29025.5'}, {'date': '2023-08-07 05:08', 'price': '29117'}, {'date': '2023-08-07 06:08', 'price': '29173.5'}, {'date': '2023-08-07 07:08', 'price': '29129.5'}, {'date': '2023-08-07 08:08', 'price': '29156.5'}, {'date': '2023-08-07 09:08', 'price': '29090'}, {'date': '2023-08-07 10:08', 'price': '29015'}, {'date': '2023-08-07 11:08', 'price': '29058.5'}, {'date': '2023-08-07 12:08', 'price': '29029.5'}, {'date': '2023-08-07 13:08', 'price': '29052'}, {'date': '2023-08-07 14:08', 'price': '29102'}, {'date': '2023-08-07 15:08', 'price': '29044'}, {'date': '2023-08-07 16:08', 'price': '29028'}, {'date': '2023-08-07 17:08', 'price': '29001.5'}, {'date': '2023-08-07 18:08', 'price': '28998'}, {'date': '2023-08-07 19:08', 'price': '28839'}, {'date': '2023-08-07 20:08', 'price': '28922'}, {'date': '2023-08-07 21:08', 'price': '28953.5'}, {'date': '2023-08-07 22:08', 'price': '29078'}, {'date': '2023-08-07 23:08', 'price': '29142.5'}, {'date': '2023-08-08 00:08', 'price': '29183'}, {'date': '2023-08-08 01:08', 'price': '29175.5'}, {'date': '2023-08-08 02:08', 'price': '29157'}, {'date': '2023-08-08 03:08', 'price': '29191.5'}, {'date': '2023-08-08 04:08', 'price': '29235'}, {'date': '2023-08-08 05:08', 'price': '29125.5'}, {'date': '2023-08-08 06:08', 'price': '29152.5'}, {'date': '2023-08-08 07:08', 'price': '29178'}, {'date': '2023-08-08 08:08', 'price': '29206'}, {'date': '2023-08-08 09:08', 'price': '29235'}, {'date': '2023-08-08 10:08', 'price': '29204'}, {'date': '2023-08-08 11:08', 'price': '29168'}, {'date': '2023-08-08 12:08', 'price': '29160.5'}, {'date': '2023-08-08 13:08', 'price': '29182.5'}, {'date': '2023-08-08 14:08', 'price': '29280'}, {'date': '2023-08-08 15:08', 'price': '29414'}, {'date': '2023-08-08 16:08', 'price': '29567'}, {'date': '2023-08-08 17:08', 'price': '29333'}, {'date': '2023-08-08 18:08', 'price': '29421.5'}, {'date': '2023-08-08 19:08', 'price': '29516.5'}, {'date': '2023-08-08 20:08', 'price': '29730'}, {'date': '2023-08-08 21:08', 'price': '29788'}, {'date': '2023-08-08 22:08', 'price': '29830'}, {'date': '2023-08-08 23:08', 'price': '29864'}, {'date': '2023-08-09 00:08', 'price': '29970.5'}, {'date': '2023-08-09 01:08', 'price': '29851.5'}, {'date': '2023-08-09 02:08', 'price': '29761'}, {'date': '2023-08-09 03:08', 'price': '29760.5'}, {'date': '2023-08-09 04:08', 'price': '29770.5'}, {'date': '2023-08-09 05:08', 'price': '29843'}, {'date': '2023-08-09 06:08', 'price': '29686'}, {'date': '2023-08-09 07:08', 'price': '29699.5'}, {'date': '2023-08-09 08:08', 'price': '29746.5'}, {'date': '2023-08-09 09:08', 'price': '29718.5'}, {'date': '2023-08-09 10:08', 'price': '29712.5'}, {'date': '2023-08-09 11:08', 'price': '29811'}, {'date': '2023-08-09 12:08', 'price': '29827'}, {'date': '2023-08-09 13:08', 'price': '29770'}, {'date': '2023-08-09 14:08', 'price': '29835'}, {'date': '2023-08-09 15:08', 'price': '29886'}, {'date': '2023-08-09 16:08', 'price': '30064.5'}, {'date': '2023-08-09 17:08', 'price': '29872'}, {'date': '2023-08-09 18:08', 'price': '29751'}, {'date': '2023-08-09 19:08', 'price': '29746.5'}, {'date': '2023-08-09 20:08', 'price': '29495.5'}, {'date': '2023-08-09 21:08', 'price': '29500'}, {'date': '2023-08-09 22:08', 'price': '29510'}, {'date': '2023-08-09 23:08', 'price': '29395.5'}, {'date': '2023-08-10 00:08', 'price': '29495'}, {'date': '2023-08-10 01:08', 'price': '29519'}, {'date': '2023-08-10 02:08', 'price': '29594'}, {'date': '2023-08-10 03:08', 'price': '29572'}, {'date': '2023-08-10 04:08', 'price': '29613.5'}, {'date': '2023-08-10 05:08', 'price': '29610.5'}, {'date': '2023-08-10 06:08', 'price': '29577.5'}, {'date': '2023-08-10 07:08', 'price': '29573.5'}, {'date': '2023-08-10 08:08', 'price': '29527.5'}, {'date': '2023-08-10 09:08', 'price': '29573.5'}, {'date': '2023-08-10 10:08', 'price': '29500'}, {'date': '2023-08-10 11:08', 'price': '29496'}, {'date': '2023-08-10 12:08', 'price': '29501'}, {'date': '2023-08-10 13:08', 'price': '29523'}, {'date': '2023-08-10 14:08', 'price': '29541'}, {'date': '2023-08-10 15:08', 'price': '29490.5'}, {'date': '2023-08-10 16:08', 'price': '29544.5'}, {'date': '2023-08-10 17:08', 'price': '29667'}, {'date': '2023-08-10 18:08', 'price': '29476'}, {'date': '2023-08-10 19:08', 'price': '29445'}]
    #b = [{'date': '2023-08-11 12:08', 'price': '29386'}, {'date': '2023-08-11 13:08', 'price': '29361.5'}, {'date': '2023-08-11 14:08', 'price': '29385.5'}, {'date': '2023-08-11 15:08', 'price': '29427.5'}, {'date': '2023-08-11 16:08', 'price': '29403.5'}, {'date': '2023-08-11 17:08', 'price': '29445'}, {'date': '2023-08-11 18:08', 'price': '29480'}, {'date': '2023-08-11 19:08', 'price': '29368.5'}, {'date': '2023-08-11 20:08', 'price': '29338'}, {'date': '2023-08-11 21:08', 'price': '29323'}, {'date': '2023-08-11 22:08', 'price': '29349.5'}, {'date': '2023-08-11 23:08', 'price': '29370.5'}, {'date': '2023-08-12 00:08', 'price': '29393.5'}, {'date': '2023-08-12 01:08', 'price': '29381.5'}, {'date': '2023-08-12 02:08', 'price': '29413.5'}, {'date': '2023-08-12 03:08', 'price': '29410.5'}, {'date': '2023-08-12 04:08', 'price': '29438.5'}, {'date': '2023-08-12 05:08', 'price': '29387'}, {'date': '2023-08-12 06:08', 'price': '29372.5'}, {'date': '2023-08-12 07:08', 'price': '29382'}, {'date': '2023-08-12 08:08', 'price': '29405'}, {'date': '2023-08-12 09:08', 'price': '29388'}, {'date': '2023-08-12 10:08', 'price': '29399.5'}, {'date': '2023-08-12 11:08', 'price': '29403.5'}, {'date': '2023-08-12 12:08', 'price': '29377'}, {'date': '2023-08-12 13:08', 'price': '29405'}, {'date': '2023-08-12 14:08', 'price': '29423'}, {'date': '2023-08-12 15:08', 'price': '29415.5'}, {'date': '2023-08-12 16:08', 'price': '29418.5'}, {'date': '2023-08-12 17:08', 'price': '29396.5'}, {'date': '2023-08-12 18:08', 'price': '29437'}, {'date': '2023-08-12 19:08', 'price': '29428'}, {'date': '2023-08-12 20:08', 'price': '29455.5'}, {'date': '2023-08-12 21:08', 'price': '29420.5'}, {'date': '2023-08-12 22:08', 'price': '29419'}, {'date': '2023-08-12 23:08', 'price': '29402'}, {'date': '2023-08-13 00:08', 'price': '29408'}, {'date': '2023-08-13 01:08', 'price': '29400.5'}, {'date': '2023-08-13 02:08', 'price': '29412'}, {'date': '2023-08-13 03:08', 'price': '29416'}, {'date': '2023-08-13 04:08', 'price': '29432.5'}, {'date': '2023-08-13 05:08', 'price': '29438'}, {'date': '2023-08-13 06:08', 'price': '29438.5'}, {'date': '2023-08-13 07:08', 'price': '29401'}, {'date': '2023-08-13 08:08', 'price': '29383.5'}, {'date': '2023-08-13 09:08', 'price': '29367'}, {'date': '2023-08-13 10:08', 'price': '29380'}, {'date': '2023-08-13 11:08', 'price': '29391'}, {'date': '2023-08-13 12:08', 'price': '29396'}, {'date': '2023-08-13 13:08', 'price': '29396'}, {'date': '2023-08-13 14:08', 'price': '29396'}, {'date': '2023-08-13 15:08', 'price': '29359'}, {'date': '2023-08-13 16:08', 'price': '29366.5'}]
    #forecast()
    #prepare_data_excel(b)
    # price = get_only_price(b)
    # print(price)
    #forecast(b)
    #forecastARIMA()
    #add_real_price(b)
    main()