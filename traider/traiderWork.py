from loguru import logger
from workYDB import Ydb

sql = Ydb()

def get_prognoz():
    rows = sql.select_query('prognoz', "type='prognoz' and side='buy'")
    for row in rows:
        print(f'{row=}')



if __name__ == '__main__':
    get_prognoz()