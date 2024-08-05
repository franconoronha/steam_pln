from bs4 import BeautifulSoup
import time

with open('./data/steamdb_ids.txt', encoding='utf-8') as f:
    html_doc = f.read()

soup = BeautifulSoup(html_doc, 'html.parser')
rows = soup.find_all('tr')
data_ids = [row.get('data-appid') for row in rows if row.get('data-appid') is not None]

print(len(data_ids), 'data IDs have been found.')

filename = f'./data/game_ids_{int(time.time())}.txt'

with open(filename, 'w', encoding='utf-8') as file:
    for data_id in data_ids:
        file.write(f'{data_id}\n')

print(f'Data IDs have been saved to {filename}')