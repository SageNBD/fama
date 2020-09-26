from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import requests
import time

class Scraper:
    
    def __init__(self, driver):
        self.page_sources = []
        self.agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
        self.header = { 'User-Agent': self.agent }
        self.driver = driver

    def reset(self):
        self.page_sources = []

    def set_date(self, date):
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(1.5)
        search_options = self.driver.find_elements_by_class_name("mn-hd-txt")

        # Opção de intervalo de tempo é o terceiro item da lista
        time_period = search_options[2]
        time_period.click()

        interval = self.driver.find_element_by_id("cdrlnk")
        interval.click()

        from_date = self.driver.find_element_by_id("OouJcb")
        from_date.clear()
        from_date.send_keys(date)

        to_date = self.driver.find_element_by_id("rzG2be")
        to_date.clear()
        to_date.send_keys(date)

        send = self.driver.find_elements_by_class_name("Ru1Ao")[0]
        send.click()

    def scrape(self, asset, date):
        # Ir para a tab do Google News.
        # window_handles = [<Google_News>, <Google_Tradutor>]
        self.driver.switch_to.window(self.driver.window_handles[0])

        # Procurar pelo nome do ativo
        search_bar = self.driver.find_element_by_id('lst-ib')
        search_bar.clear()
        search_bar.send_keys(asset + Keys.ENTER)
        time.sleep(1.0)

        # Adiciona o código-fonte à lista
        self.page_sources.append(self.driver.page_source)

        # ----------------------------------------------------------------
        # TIRE ESSE COMENTÁRIO PARA OBTER MAIS DE UMA PÁGINA DE RESULTADOS
        # ----------------------------------------------------------------
        # table = self.driver.find_element_by_xpath("//table[@class='AaVjTc']")
        # next_pages = table.find_elements_by_class_name("fl")
        # urls = [page.get_attribute("href") for page in next_pages]
        # for url in urls:
        #     self.driver.get(url)
        #     time.sleep(1.0)
        #     self.page_sources.append(self.driver.page_source)

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