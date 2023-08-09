
from statistics import mean
from datetime import datetime, timedelta
from pytrends.request import TrendReq
from pprint import pprint
# Создайте экземпляр объекта TrendReq
pytrends = TrendReq(tz=1000)
keywords = ['BTC USD','buy bitcoin']
# Установите параметры запроса
#pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')
pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')
# Получите данные о трендах
#def get_trends()-> list:
def get_trends():
    trend_data = pytrends.interest_over_time()
    #print(trend_data.name)
    prepareTrends = []
    testDict = {}
    for i in range(0,168):
        try: 
            b = trend_data.index[i].strftime('%Y-%m-%d %H:%M:%S')
        except IndexError:
            break

        #b = trend_data.index[i]
        b = datetime.strptime(b,'%Y-%m-%d %H:%M:%S') + timedelta(hours=3)
        b = b.strftime('%Y-%m-%d %H:%M:%S')
        #b = trend_data.index[i].strftime('%Y-%m-%d') 
        #print(b)
        #NOTE
        # select name from analit where datetime > date('1990-03-15') 
        #по часам
        # prepareTrends.append([b])#.values.tolist())
        # prepareTrends[i].append(trend_data['BTC USD'][i])#.values.tolist())
        # prepareTrends[i].append(trend_data['buy bitcoin'][i])#.values.tolist())

        #prepareTrends.append([b])#.values.tolist())
        btc = trend_data['BTC USD'][i]#.values.tolist())
        buy = trend_data['buy bitcoin'][i]#.values.tolist())
        #print(trend_data.iloc[i][3])#.values.tolist())
        try:
            testDict[b][0].append(btc)
            testDict[b][1].append(buy)
        except:
            testDict.setdefault(b,[[btc],[buy]])
    result = {}
    for date, arrays in testDict.items():
        averages = [mean(array) for array in arrays]
        result[date] = averages

    #print(result)        
    return result
    #return prepareTrends
    #return testDict 

if __name__ == '__main__':
    a = get_trends()
    pprint(a)
