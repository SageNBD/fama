import requests
from bs4 import BeautifulSoup
import datetime

asset = 'itau'
date = datetime.datetime(2016, 1, 1)

url = (
        f"https://www.google.com/search?q={asset}&tbs=cdr%3A1"
        f"%2Ccd_min%3A{date.month}%2F{date.day}%2F{date.year}"
        f"%2Ccd_max%3A{date.month}%2F{date.day}%2F{date.year}&tbm=nws"
      )

agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
header = { 'User-Agent': agent }
source = requests.get(url, headers=header)

soup = BeautifulSoup(source.content, "lxml")

#noticias = soup.find_all("div", {"class": "g"})
noticias = soup.find_all("div", {"class": "hI5pFf"})

print(f"num_noticias = {len(noticias)}")
#print(f"noticias = {noticias}")

data = []

for noticia in noticias:
    news_data = {}

    #headline = noticia.find("a", {"class": "l lLrAF"}).text 
    headline = noticia.find("div", {"class": "JheGif jBgGLd"}).text

    #source = noticia.find("span", {"class": "xQ82C e8fRJf"}).text 
    source = noticia.find("div", {"class": "XTjFC WF4CUc"}).text

    #body = noticia.find("div", {"class": "st"}).text
    body = noticia.find("div", {"class": "Y3v8qd"}).text

    news_data['headline'] = headline
    news_data['source'] = source
    news_data['body'] = body

    data.append(news_data)

for d in data:
    for k, v in d.items():
        print(k, v)
