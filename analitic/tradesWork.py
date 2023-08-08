

from pytrends.request import TrendReq

# Создайте экземпляр объекта TrendReq
pytrends = TrendReq()
keywords = ['BTC USD','buy bitcoin']
# Установите параметры запроса
pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo='', gprop='')
# Получите данные о трендах
trend_data = pytrends.interest_over_time()

print(trend_data['BTC USD'][1][0])#.values.tolist())