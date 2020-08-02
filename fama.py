from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import datetime
import time
import requests

class Scraper:

    def __init__(self, driver):
        self.page_sources = []
        driver.get(f"https://google.com/search?q=quantamental&source=lnms&tbm=nws")
        tools = driver.find_element_by_id("hdtb-tls")
        tools.click()

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

    def scrape_requests(self, driver, asset, date): 
        prefix = f"https://www.google.com/search?q={asset}&tbs=cdr%3A1"
        start = f"%2Ccd_min%3A{date.month}%2F{date.day}%2F{date.year}"
        end = f"%2Ccd_max%3A{date.moth}%2F{date.day}%2F{date.year}&tbm=nws"
        url = prefix + start + end

    def extract_headlines(self):
        data = []
        for page_num, page_source in enumerate(self.page_sources):
            soup = BeautifulSoup(page_source, 'lxml')
            noticias = soup.find_all("div", {"class": "g"})
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
        return data

class Translator():

    def __init__(self, driver):
        driver.execute_script('''
            window.open('https://translate.google.com/?hl=pt-BR', '_blank')
            '''
        )
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(1.0)

        self.text_input = None
        while not self.text_input: # Espera a página carregar
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

    def translate(self, headline, body):
        # Ir para a tab do Google Tradutor.
        # window_handles = [<Google_News>, <Google_Tradutor>]
        driver.switch_to.window(driver.window_handles[1])

        if headline:
            print(f"headline = {headline}", end='')
            # Translate headline text
            self.text_input.send_keys(headline)
            time.sleep(1.5)

            text_output = None
            while not text_output:
                try:
                    text_output = driver.find_elements_by_class_name("translation")[0]
                except NoSuchElementException:
                    time.sleep(1.0)
            headline = text_output.find_element_by_tag_name("span").text
            self.text_input.clear()

        # Translate body text
        self.text_input.send_keys(body)
        time.sleep(1.5)
        print(f"body = {body}")

        text_output = None
        while not text_output:
            try:
                text_output = driver.find_elements_by_class_name("translation")[0]
                body = text_output.find_element_by_tag_name("span").text
            except NoSuchElementException:
                time.sleep(1.0)
            except IndexError:
                return (headline, "")
        self.text_input.clear()

        return (headline, body)

class MarketData:

    def __init__(self, date, asset):
        self.df = yf.download(asset, period="1d", interval="5m")

driver = webdriver.Firefox()
scraper = Scraper(driver)
translator = Translator(driver)

today = datetime.datetime(2015, 12, 31) # Mudar a janela de tempo

assets = ['itau', 'ambev', 'petrobras']
#assets = ['itau']

start_time = time.time()
for i in range(2):
    today += datetime.timedelta(days=1)
    
    print(f"\t{today.strftime('%d/%m/%Y')}")
    scraper.set_date(today.strftime('%m/%d/%Y'))
    for asset in assets:
        print("\t" + asset)
        scraper.scrape(driver, asset, today.strftime('%m/%d/%Y'))
        data = scraper.extract_headlines()

        asset_dir_name = '_'.join(asset.split())
        with open(f"dados/{asset_dir_name}/{today.strftime('%d_%m')}_pt.txt", "w") as f:
            for d in data:
                for key, val in d.items():
                    f.write(f"{key}: {val}\n")
                f.write("\n")

        if not data: # Lista vazia. Não há notícias para traduzir
            continue

        for d in data:
            if asset not in d['headline'].lower(): # Nome do ativo não está na manchete
                headline, body = translator.translate("", d['body'])
            else:
                headline, body = translator.translate(d['headline'], d['body'])
            with open(f"dados/{asset_dir_name}/{today.strftime('%d_%m')}_en.txt", "w") as f:
                f.write(f"{headline}\n{body}\n\n")
        scraper.reset()

end_time = time.time()
print(f"Execução demorou {end_time - start_time}s")

