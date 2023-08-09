

from pytrends.request import TrendReq
from pprint import pprint
# Создайте экземпляр объекта TrendReq
pytrends = TrendReq()
keywords = ['BTC USD','buy bitcoin']
# Установите параметры запроса
#pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')
pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')
# Получите данные о трендах
def get_trends():
    trend_data = pytrends.interest_over_time()
    #print(trend_data.name)
    prepareTrends = []
    for i in range(0,168):
        b = trend_data.index[i].strftime('%Y-%m-%d %H:%M:%S') 
        #print(b)
        prepareTrends.append([b])#.values.tolist())
        prepareTrends[i].append(trend_data['BTC USD'][i])#.values.tolist())
        prepareTrends[i].append(trend_data['buy bitcoin'][i])#.values.tolist())
        #print(trend_data.iloc[i][3])#.values.tolist())
    return prepareTrends

if __name__ == '__main__':
    a = get_trends()
    pprint(a)
