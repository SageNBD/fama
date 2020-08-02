import requests
from bs4 import BeautifulSoup
import datetime

asset = 'itau'
date = datetime.datetime(2016, 1, 1)

prefix = f"https://www.google.com/search?q={asset}&tbs=cdr%3A1"
start = f"%2Ccd_min%3A{date.month}%2F{date.day}%2F{date.year}"
end = f"%2Ccd_max%3A{date.month}%2F{date.day}%2F{date.year}&tbm=nws"
url = prefix + start + end

source = requests.get(url)

soup = BeautifulSoup(source.text, "lxml")
print(soup.prettify())
noticias = soup.find_all("div", {"class": "g"})
print(f"num_noticias = {len(noticias)}")
print(f"noticias = {noticias}")

data = []

for noticia in noticias:
    news_data = {}

    headline = noticia.find("a", {"class": "l lLrAF"}).text 
    source = noticia.find("span", {"class": "xQ82C e8fRJf"}).text 
    body = noticia.find("div", {"class": "st"}).text

    news_data['headline'] = headline
    news_data['source'] = source
    news_data['body'] = body
    news_data['page'] = page_num

    data.append(news_data)

for d in data:
    for k, v in d.items():
        print(k, v)
