import urllib.request
import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer


SEED_URLS = ['https://gov.si', 'https://evem.gov.si', 'https://e-uprava.gov.si', 'https://e-prostor.gov.si']
WEB_PAGE_ADDRESS =SEED_URLS[2]              #trenutno samo za eno
USER_AGENT = 'fri-wier-KJB'
WEB_DRIVER_LOCATION = "./chromedriver"
TIMEOUT = 5
REGEX = "^(?:https?:\/\/)?(?:[^\.]+\.)?gov\.si(\/.*)?$"

TAGS = ['a', 'link']


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

    #page_msg = driver.find_element_by_class_name("element-title")

    #print(f"Web page message: '{page_msg.text}'")

    ########################################################################################
    # Fetching links and images
    #parser = 'html.parser'
    #soup = BeautifulSoup(html, parser)
    #print(f"Web page links:", fetchLinks(soup))
    #print(f"Web page images:", fetchImages(soup))

    #Crawl

    """Starting from this URL, crawl the web until
       you have collected maxurls URLS, then return them
       as a set"""

    links = crawl(SEED_URLS[1], 20)
    print("Collected ", len(links), " links:")
    for link in links:
        print(link)

    driver.close()


def get_page(url):
    """Get the text of the web page at the given URL
    return a string containing the content"""

    fd = urllib.request.urlopen(url)
    content = fd.read()
    fd.close()

    return content.decode('utf8')

def get_links(url):
    """Scan the text for http URLs and return a set
    of URLs found, without duplicates"""

    # look for any http URL in the page
    links = set()

    parser = 'html.parser'
    text = get_page(url)
    soup = BeautifulSoup(text, parser)
    try:

        for link in soup.find_all('a'):
            if 'href' in link.attrs:
                newurl = link.attrs['href']
                # resolve relative URLs
                if newurl.startswith('/'):
                    newurl = urljoin(url, newurl)
                # ignore any URL that doesn't now start with http
                if newurl.startswith('http'):
                    if re.search(REGEX, newurl):
                        links.add(newurl)
    except ValueError:
        print("Error when trying to fetch images")

    return links

def crawl(url, maxurls=20):
    """Starting from this URL, crawl the web until
    you have collected maxurls URLS, then return them
    as a set"""

    urls = set([url])
    while(len(urls) < maxurls):
        # remove a URL at random
        url = urls.pop()
        print("URL: ", url)
        links = get_links(url)
        urls.update(links)
        # add the url back to the set
        urls.add(url)

    return urls


def get_images(url):
    """Scan the text for images and return a set
    of images, without duplicates"""

    # look for any http URL in the page
    images = set()

    text = get_page(url)
    soup = BeautifulSoup(text)
    try:

        for link in soup.find_all('img'):
            if 'src' in link.attrs:
                newimg = link.attrs['src']
                # resolve relative URLs
                if newimg.startswith('/'):
                    newimg = urljoin(url, newimg)
                    images.add(newimg)
    except ValueError:
        print("Error when trying to fetch images")

    return images



if __name__ == "__main__":
    crawler()