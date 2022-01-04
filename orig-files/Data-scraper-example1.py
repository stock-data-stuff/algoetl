import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from itertools import groupby

url = 'https://fansided.com/2016/08/11/nba-schedule-2016-national-tv-games/'
soup = BeautifulSoup(requests.get(url).content, 'html.parser')

days = 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
data = soup.select_one('.article-content p:has(br)').get_text(strip=True, separator='|').split('|')

dates, last = {}, ''
for v, g in groupby(data, lambda k: any(d in k for d in days)):
    if v:
        last = [*g][0]
        dates[last] = []
    else:
        dates[last].extend([re.findall(r'([\d:]+ [AP]M) (.*?)/(.*?) (.*)', d)[0] for d in g])

all_data = {'Date':[], 'Time': [], 'Team 1': [], 'Team 2': [], 'Network': []}
for k, v in dates.items():
    for time, team1, team2, network in v:
        all_data['Date'].append(k)
        all_data['Time'].append(time)
        all_data['Team 1'].append(team1)
        all_data['Team 2'].append(team2)
        all_data['Network'].append(network)

df = pd.DataFrame(all_data)
print(df)

df.to_csv('data.csv')