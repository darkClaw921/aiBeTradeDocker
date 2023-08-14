import pandas as pd

# Ваш список данных
data = [{'date': '2023-08-03 00:08', 'price': '29128'}, {'date': '2023-08-03 01:08', 'price': '29182.5'}]

# Создаем DataFrame
df = pd.DataFrame(data)

# Сохраняем DataFrame в файл Excel
df.to_excel('data.xlsx', index=False)