# import numpy as np
# import matplotlib.pyplot as plt
from loguru import logger
from workYDB import Ydb
# import statsmodels.api as sm
# date = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198]
# # price = np.array(price)
# price = [29452.0, 29533.5, 29560.0, 29454.0, 29402.5, 29264.5, 29324.0, 29024.0, 29132.5, 29139.5, 29150.0, 29128.0, 29182.5, 29179.5, 29180.5, 29158.5, 29239.0, 29168.0, 29164.0, 29114.5, 29132.5, 29067.5, 29020.0, 29105.5, 29144.5, 29165.0, 29132.5, 29095.5, 29179.0, 29394.0, 29247.0, 29298.5, 29232.0, 29278.0, 29279.0, 29296.0, 29243.0, 29235.5, 29186.0, 29233.0, 29202.0, 29164.0, 29158.0, 29201.0, 29235.0, 29186.5, 29206.5, 29176.0, 29189.5, 29154.0, 29160.5, 29205.0, 29223.5, 29242.5, 29254.5, 29250.0, 29188.5, 29047.5, 29009.0, 28942.0, 29032.0, 29027.5, 29088.5, 29090.0, 29041.0, 29058.5, 29054.5, 29014.0, 29063.0, 29031.0, 29020.0, 29060.0, 29035.5, 29032.5, 29024.0, 28998.0, 29013.5, 29054.0, 29018.0, 29013.0, 29037.5, 29050.0, 29044.0, 29038.0, 29055.5, 29069.5, 29053.5, 29044.5, 29020.0, 29047.0, 29039.5, 29055.0, 29081.5, 29047.0, 29073.5, 29094.0, 29059.0, 29049.0, 29054.0, 29014.5, 29000.0, 29023.0, 28991.0, 29064.5, 29073.5, 29074.0, 29070.0, 29114.0, 29061.5, 29078.5, 29064.0, 29025.5, 29117.0, 29173.5, 29129.5, 29156.5, 29090.0, 29015.0, 29058.5, 29029.5, 29052.0, 29102.0, 29044.0, 29028.0, 29001.5, 28998.0, 28839.0, 28922.0, 28953.5, 29078.0, 29142.5, 29183.0, 29175.5, 29157.0, 29191.5, 29235.0, 29125.5, 29152.5, 29178.0, 29206.0, 29235.0, 29204.0, 29168.0, 29160.5, 29182.5, 29280.0, 29414.0, 29567.0, 29333.0, 29421.5, 29516.5, 29730.0, 29788.0, 29830.0, 29864.0, 29970.5, 29851.5, 29761.0, 29760.5, 29770.5, 29843.0, 29686.0, 29699.5, 29746.5, 29718.5, 29712.5, 29811.0, 29827.0, 29770.0, 29835.0, 29886.0, 30064.5, 29872.0, 29751.0, 29746.5, 29495.5, 29500.0, 29510.0, 29395.5, 29495.0, 29519.0, 29594.0, 29572.0, 29613.5, 29610.5, 29577.5, 29573.5, 29527.5, 29573.5, 29500.0, 29496.0, 29501.0, 29523.0, 29541.0, 29490.5, 29544.5, 29667.0, 29476.0, 29445.0]

# datePrognoz = [n for n in range(199, 301)]
sql = Ydb()
@logger.catch
def get_forecast_SARIMAX(data, dayForecast: int=0, persentCoridor:float=0.0075):
#def main11():
    #work
    import numpy as np
    import pandas as pd
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from datetime import datetime
    from helper import time_epoch
  
    prices = [float(item['price']) for item in data]
    dates = pd.to_datetime([item['date'] for item in data])
    # series = pd.Series(prices, index=dates)

    print(f'{prices=}')
    print(f'{dates=}')
    
    #series = pd.Series([29396, 29396], index=pd.to_datetime(['2023-08-13 12:08', '2023-08-13 13:08']))

    series = pd.Series(prices, index=dates)

    model = SARIMAX(series, order=(1, 0, 1), seasonal_order=(1, 1, 1, 20), validate_specification=False)

    # Обучение модели
    model_fit = model.fit()
    n = dayForecast
    # Получение предсказанных значений
    pred = model_fit.predict(len(series), len(series)+n) # где n - количество точек для предсказания
    #print(pred.keys(), pred.values[0])
    print(f'{pred=}')
    price = pred.values[0]
    lower_bound= price-(price*persentCoridor)
    upper_bound= price+(price*persentCoridor)
    print(f'{lower_bound=}')
    print(f'{upper_bound=}')
    #DealPrice = TargetPrice - RiskPercent ДО ЦЕНЫ TPDownLevel
    dateClose =str(pred.keys()[0])
    datetime_obj = datetime.strptime(dateClose, '%Y-%m-%d %H:%M:%S')
    formatted_timestamp = datetime_obj.strftime('%Y-%m-%dT%H:%M:%SZ')
    row = {
            'time_epoh': time_epoch(),
            #'date_close': str(dateClose).replace(' ','T')+'Z',
            'date_close': formatted_timestamp,
            'price_close': pred.values[0],
            'strat': 'strat1',
            'type': 'prognoz',
            'lower_price':lower_bound,
            'upper_price':upper_bound,
        } 
        #sql.replace_query('analitic', row)
    sql.replace_query('analitic', row)
    return price,lower_bound,upper_bound, pred.keys()[0] 

if __name__ == '__main__':
   #get_forecast_SARIMAX()
   pass