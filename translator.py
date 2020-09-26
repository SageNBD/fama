from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
import subprocess

class Translator():
    
    def __init__(self, driver):
        self.driver = driver
        self.driver.get('https://translate.google.com/?hl=pt-BR')
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
                    text_output = self.driver.find_elements_by_class_name("translation")[0]
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
                text_output = self.driver.find_elements_by_class_name("translation")[0]
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