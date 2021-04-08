import csv
import io
import os
import zipfile

import redis
import requests
from datetime import datetime
from django.conf import settings

redis_instance = redis.StrictRedis(host=settings.REDIS_URL.hostname, port=settings.REDIS_URL.port, charset="utf-8",
                                   decode_responses=True)


def get_equity_data():
    file_name = f'EQ{datetime.today().strftime("%d%m%y")}'
    # file_name = f'EQ{(datetime.today() - timedelta(days=1)).strftime("%d%m%y")}'
    url = f'https://www.bseindia.com/download/BhavCopy/Equity/{file_name}_CSV.ZIP'
    response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'})
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    zip_file.extractall(os.path.join(os.getcwd()))
    with open(f"{file_name}.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line_count, row in enumerate(csv_reader):
            if line_count == 0:
                continue
            # key: name, value: name, code, open, high, low, close
            stock_name = row[1].rstrip().lstrip()
            redis_instance.hmset(stock_name,
                                 {'name': stock_name, 'code': row[0], 'open': round(float(row[4]), 2),
                                  'high': round(float(row[5]), 2), 'low': round(float(row[6]), 2),
                                  'close': round(float(row[7]), 2)})
            redis_instance.expire(stock_name, settings.REDIS_TIME_OUT)
    redis_instance.set(name='last_updated', value=datetime.now().strftime('%d/%m/%YT%H:%M:%S'),
                       ex=settings.REDIS_TIME_OUT)
    os.remove(os.path.join(os.getcwd(), f"{file_name}.csv"))
