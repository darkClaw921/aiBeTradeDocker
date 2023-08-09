
from tradesWork import get_trends
import requests
from pprint import pprint
from loguru import logger
from helper import array, get_average
from workYDB import Ydb

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
    #print(req.text)
    pricePairHour = eval(req.text)
    pricePairHour = array(pricePairHour)
    #print(f'{pricePairHour=}')
    #b=req1.text
    # print(b)
    pprint(trends)
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
    if onlyNOW: 
        sql.replace_query('strateg', row)
        prognoz = get_prognoz(dateStart, dateEnd)
        return prognoz 
        return 0
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


def main():
    #pr = get_prognoz('2023-08-02', '2023-08-04')
    pr = add_7d_trends_to_YDB(onlyNOW=True)
    print(f'{pr=}')

if __name__ == "__main__":

    main()