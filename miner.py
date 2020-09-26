from translator import Translator
from scraper import Scraper
from selenium import webdriver
from db import Mongo
import datetime
import time
import requests
import subprocess
        
if __name__ == "__main__":
    driver = webdriver.Firefox()
    scraper = Scraper(driver)
    translator = Translator(driver)

    assets = ['itau', 'ambev', 'petrobras']
    db = Mongo(assets)

    today = datetime.datetime(2019, 4, 9) # Mudar a janela de tempo
    end_date = datetime.datetime(2020, 1, 1)
    total_days = (end_date - today).days

    for i in range(total_days):
        days_left = (end_date - today).days
        progress = ((i + 1) / (total_days * 1.0)) * 100

        print(f"Today is {today.strftime('%d/%m/%Y')}. There are {days_left} days left")
        print(f"Progress: {progress}%")

        for asset in assets:
            data = scraper.scrape_requests(asset, today)

            if not data: # Lista vazia. Não há notícias para traduzir
                print(f"didnt find any data for {asset} on {today.strftime('%d/%m/%Y')}")
                continue

            for d in data: # Traduz a manchete
                translator.translate(d)

            db.asset_collection[asset].insert_many(data)

        today += datetime.timedelta(days=1)

    driver.close()

