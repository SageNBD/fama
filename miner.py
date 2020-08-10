from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import time
import requests
import subprocess

class Scraper:

    def __init__(self):
        self.page_sources = []
        self.agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
        self.header = { 'User-Agent': self.agent }

    def reset(self):
        self.page_sources = []

    def set_date(self, date):
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1.5)
        search_options = driver.find_elements_by_class_name("mn-hd-txt")

        # Opção de intervalo de tempo é o terceiro item da lista
        time_period = search_options[2]
        time_period.click()

        interval = driver.find_element_by_id("cdrlnk")
        interval.click()

        from_date = driver.find_element_by_id("OouJcb")
        from_date.clear()
        from_date.send_keys(date)

        to_date = driver.find_element_by_id("rzG2be")
        to_date.clear()
        to_date.send_keys(date)

        send = driver.find_elements_by_class_name("Ru1Ao")[0]
        send.click()

    def scrape(self, driver, asset, date):
        # Ir para a tab do Google News.
        # window_handles = [<Google_News>, <Google_Tradutor>]
        driver.switch_to.window(driver.window_handles[0])

        # Procurar pelo nome do ativo
        search_bar = driver.find_element_by_id('lst-ib')
        search_bar.clear()
        search_bar.send_keys(asset + Keys.ENTER)
        time.sleep(1.0)

        # Adiciona o código-fonte à lista
        self.page_sources.append(driver.page_source)

        # ----------------------------------------------------------------
        # TIRE ESSE COMENTÁRIO PARA OBTER MAIS DE UMA PÁGINA DE RESULTADOS
        # ----------------------------------------------------------------
        # table = driver.find_element_by_xpath("//table[@class='AaVjTc']")
        # next_pages = table.find_elements_by_class_name("fl")
        # urls = [page.get_attribute("href") for page in next_pages]
        # for url in urls:
        #     driver.get(url)
        #     time.sleep(1.0)
        #     self.page_sources.append(driver.page_source)

    def scrape_requests(self, asset, date): 
        url = (
                f"https://www.google.com/search?q={asset}&tbs=cdr%3A1"
                f"%2Ccd_min%3A{date.month}%2F{date.day}%2F{date.year}"
                f"%2Ccd_max%3A{date.month}%2F{date.day}%2F{date.year}&tbm=nws"
              )

        source = requests.get(url, headers=self.header)
        soup = BeautifulSoup(source.content, "lxml")
        
        noticias = soup.find_all("div", {"class": "hI5pFf"})

        data = []
        for noticia in noticias:
            news_data = {}

            headline = noticia.find("div", {"class": "JheGif jBgGLd"}).text
            source = noticia.find("div", {"class": "XTjFC WF4CUc"}).text
            body = noticia.find("div", {"class": "Y3v8qd"}).text

            news_data['headline'] = headline
            news_data['source'] = source
            news_data['body'] = body
            news_data['asset'] = asset
            news_data['date'] = date.strftime('%d/%m/%y')

            data.append(news_data)
        return data

    def extract_headlines(self, today):
        data = []
        for page_num, page_source in enumerate(self.page_sources):
            soup = BeautifulSoup(page_source, 'lxml')

            noticias = soup.find_all("div", {"class": "hI5pFf"})
            for noticia in noticias:
                news_data = {}
            
                headline = noticia.find("div", {"class": "JheGif jBgGLd"}).text
                source = noticia.find("div", {"class": "XTjFC WF4CUc"}).text
                body = noticia.find("div", {"class": "Y3v8qd"}).text

                news_data['headline'] = headline
                news_data['source'] = source
                news_data['body'] = body
                news_data['page'] = page_num
                news_data['date'] = today.strftime("%d/%m/%y")

                data.append(news_data)
        return data

class Translator():

    def __init__(self, driver):
        driver.get('https://translate.google.com/?hl=pt-BR')
        time.sleep(1.0)

        self.text_input = None
        while not self.text_input: # Espera o elmento da página carregar
            try:
                self.text_input = driver.find_element_by_id("source")
            except NoSuchElementException:
                time.sleep(1.0)

        self.left_panel = driver.find_elements_by_class_name("sl-sugg")[0]
        self.right_panel = driver.find_elements_by_class_name("tl-sugg")[0]

        self.portugues = self.left_panel.find_element_by_id("sugg-item-pt")
        self.portugues.click()
        self.ingles = self.right_panel.find_element_by_id("sugg-item-en")
        self.ingles.click()

    def translate(self, news_data):
        # Ir para a tab do Google Tradutor.
        # window_handles = [<Google_News>, <Google_Tradutor>]
        #driver.switch_to.window(driver.window_handles[1])

        if news_data['headline']:
            # Translate headline text
            self.text_input.send_keys(news_data['headline'])
            time.sleep(1.5)

            text_output = None
            while not text_output:
                try:
                    text_output = driver.find_elements_by_class_name("translation")[0]
                except NoSuchElementException:
                    time.sleep(1.0)
                except IndexError:
                    time.sleep(1.0)
                except:
                    break
            try:
                news_data['headline'] = text_output.find_element_by_tag_name("span").text
            except NoSuchElementException:
                news_data['headline'] = ''
            except: 
                news_data['headline'] = ''

            self.text_input.clear()

        # Translate body text
        self.text_input.send_keys(news_data['body'])
        time.sleep(1.5)

        text_output = None
        while not text_output:
            try:
                text_output = driver.find_elements_by_class_name("translation")[0]
                news_data['body'] = text_output.find_element_by_tag_name("span").text
            except NoSuchElementException:
                time.sleep(1.0)
            except StaleElementReferenceException:
                break
            except IndexError:
                break
            except:
                break
        self.text_input.clear()
    
    def translate_by_CLI(self, headline, body):
        if headline: # Transforma pra string e retira o '\n'
            output = subprocess.check_output(['trans', '-b', headline])
            headline = output.decode('utf-8').split() 

        output = subprocess.check_output(['trans', '-b', body])

        return (headline, body)
        
if __name__ == "__main__":
    # Class Setup
    driver = webdriver.Firefox()
    scraper = Scraper()
    translator = Translator(driver)

    # MongoDB Setup
    client = MongoClient('localhost', 27017)
    db = client.fama

    # news = db.test_collection
    assets = ['itau', 'ambev', 'petrobras']

    asset_collection = {} # Create collection for each asset
    for asset in assets:
        asset_collection[asset] = db[asset]

    today = datetime.datetime(2019, 4, 9) # Mudar a janela de tempo
    end_date = datetime.datetime(2020, 1, 1)
    total_days = (end_date - today).days

    start_time = time.time()
    for i in range(total_days):
        days_left = (end_date - today).days
        progress = ((i + 1) / (total_days * 1.0)) * 100

        print(f"Today is {today.strftime('%d/%m/%Y')}. There are {days_left} days left")
        print(f"Progress: {progress}%")

        for asset in assets:
            data = scraper.scrape_requests(asset, today)

            if not data: # Lista vazia. Não há notícias para traduzir
                print('didnt find any data')
                continue

            for d in data: # Traduz a manchete
                translator.translate(d)

            asset_collection[asset].insert_many(data)

        today += datetime.timedelta(days=1)

    end_time = time.time()
    driver.close()
    print(f'Execuçao demorou {end_time - start_time}s')

