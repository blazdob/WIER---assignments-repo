import urllib.request
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib.request
from bs4 import BeautifulSoup


SEED_URLS = ['http://gov.si', 'http://evem.gov.si', 'http://e-uprava.gov.si', 'http://e-prostor.gov.si']
WEB_PAGE_ADDRESS =SEED_URLS[0]              #trenutno samo za eno
USER_AGENT = 'fri-wier-KJB'
WEB_DRIVER_LOCATION = "./chromedriver"
TIMEOUT = 5


def crawler():
    
    #-------------------------------ČE TEGA NI POTEM SE OSTALE STRANI NE ODPREJO (TO NI ZA KONČNO VERZIJO KER NE PREVERJAŠ)----------------------
    import os, ssl
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context
    #-------------------------------ČE TEGA NI POTEM SE OSTALE STRANI NE ODPREJO (TO NI ZA KONČNO VERZIJO KER NE PREVERJAŠ)----------------------
    
    request = urllib.request.Request(
        WEB_PAGE_ADDRESS, 
        headers={'User-Agent': 'fri-wier-KJB'}
    )

    with urllib.request.urlopen(request) as response: 
        html = response.read().decode("utf-8")
        print(f"Retrieved Web content: \n\n'\n{html}\n'")

    chrome_options = Options()
    # If you comment the following line, a browser will show ...
    chrome_options.add_argument("--headless")

    #Adding a specific user agent
    chrome_options.add_argument("user-agent=fri-wier-KJB")

    print(f"Retrieving web page URL '{WEB_PAGE_ADDRESS}'")
    driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=chrome_options)
    driver.get(WEB_PAGE_ADDRESS)

    # Timeout needed for Web page to render (read more about it)
    time.sleep(TIMEOUT)

    html = driver.page_source

    print(f"Retrieved Web content (truncated to first 900 chars): \n\n'\n{html[:900]}\n'\n")

    page_msg = driver.find_element_by_class_name("element-title")

    print(f"Web page message: '{page_msg.text}'")

    driver.close()


if __name__ == "__main__":
    crawler()