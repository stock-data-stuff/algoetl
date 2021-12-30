#!/usr/bin/env python3

# import external pandas_datareader library with alias of web
import pandas_datareader as web
import csv
import requests

# import datetime internal datetime module
# datetime is a Python module
import datetime

# datetime.datetime is a data type within the datetime module
start = datetime.datetime(1990, 1, 1)
end = datetime.datetime(2021, 12, 18)

# DataReader method name is case sensitive
df = web.DataReader("VIX", 'yahoo', start, end)

# invoke to_csv for df dataframe object from
# DataReader method in the pandas_datareader library

# ..\first_yahoo_prices_to_csv_demo.csv must not
# be open in another app, such as Excel

df.to_csv('VIX.csv')

# DataReader method name is case sensitive
df = web.DataReader("SPY", 'yahoo', start, end)

# invoke to_csv for df dataframe object from
# DataReader method in the pandas_datareader library

# ..\first_yahoo_prices_to_csv_demo.csv must not
# be open in another app, such as Excel

df.to_csv('SPY.csv')

CSV_URL = 'https://markets.newyorkfed.org/read?productCode=30&startDt=2021-12-22&endDt=2021-12-22&query=details&holdingTypes=bills,notesbonds,frn,tips,cmbs,agency%20debts&format=csv'

response = requests.get(CSV_URL)

with open('FED_Soma.csv', 'w') as f:
    writer = csv.writer(f)
    for line in response.iter_lines():
        writer.writerow(line.decode('utf-8').split(','))

# with requests.get(CSV_URL, stream=True) as r:
 #           lines = (line.decode('utf-8') for line in r.iter_lines())
  #          for row in csv.reader(lines):
   #             print(row)
