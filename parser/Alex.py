import requests
import bs4
from model1 import analize
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import ui
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import json


def get_cards(gender: str, url: str, attempts: int) -> list:
    # send request
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
    html = requests.get(url, headers=headers).text
    # parse request
    
    driver = webdriver.Firefox()
    driver.get(url)
    button_element = None

    for i in range(attempts):
        try:
            button_element = ui.WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".desktop ._showMore_z1yqr_2")))
        except:
            button_element = None
                
        try:
            button_element.click()
        except:
            continue
        sleep(3)

    html = driver.page_source
    driver.quit()
    
        
    result = []  # cards[card[card_link, img_link]]
    soup: bs4.BeautifulSoup = bs4.BeautifulSoup(html, "html.parser")
    catalog = soup.find("div", class_="grid__catalog").find_all("div")
    full = len(catalog)
    print('\n' + str(full) + '\n')
    ind = 0
    for card in catalog:
        ind = ind + 1
        try:
            card_link = card.find("a").get("href")
            img_link = card.find("img").get("src")
            print(f'https:{img_link} ({gender} : {round(ind / full * 100, 2)} %)')
            try:
                data = requests.get(f'https:{img_link}').content
            except:
                continue
            with open('img.jpg', 'wb') as img:
                img.truncate()
                
            with open('img.jpg', 'wb') as img:
                img.write(data)
            
            try: 
                model_res = analize('img.jpg')[0]
                del model_res[0]
                result.append((f"https://www.lamoda.ru{card_link}", model_res[0], model_res[1]))
            except:
                continue
        except AttributeError:
            pass
    return result


def load_to_json(filename: str, male_tump: tuple, female_tump: tuple) -> None: 
    target_dict = {'Male': male_tump, 'Female': female_tump}
        
    with open(filename, 'w') as file_:
        json.dump(target_dict, file_)
        
    print()
    print(target_dict)
    print('data uploaded')
    return None


if __name__ == "__main__":
    female_url = "https://www.lamoda.ru/c/355/clothes-zhenskaya-odezhda"
    male_url = "https://www.lamoda.ru/c/477/clothes-muzhskaya-odezhda"
    
    load_to_json('catalog.json', get_cards('Male', male_url, 130), get_cards('Female', female_url, 130))