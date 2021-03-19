import urllib.request
import time
import re
import logging
import requests
import hashlib
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
from email.utils import parsedate_to_datetime

from . import config


SEED_URLS = ['https://gov.si', 'https://evem.gov.si', 'https://e-uprava.gov.si', 'https://e-prostor.gov.si']
WEB_PAGE_ADDRESS =SEED_URLS[2]              #trenutno samo za eno
WEB_DRIVER_LOCATION = "./chromedriver"
TIMEOUT = 5
REGEX = "^(?:https?:\/\/)?(?:[^\.]+\.)?gov\.si(\/.*)?$"

TAGS = ['a', 'link']

headers = {'User-Agent': config.USER_AGENT}
logger = logging.getLogger(__name__)


def crawl_page(frontier, scheduler, page, db):
    logger.debug("crawling on pageid({}) at {} on siteid({})".format(page.id, page.url, page.siteid))

    # fetch head
    logger.debug("waiting on siteid({})".format(page.siteid))
    scheduler.wait_site(page.siteid)
    response = requests.head(page.url, headers=headers)
    access = datetime.datetime.now()
    logger.debug("sent HEAD request to pageid({}) at URL {}".format(page.id, page.url))

    # instructions say that 4xx and 5xx could be checked several times later,
    # page type "FRONTIER" could be used for that since frontier uses null
    # fields to identify pages in frontier
    if response.status_code >= 400:
        logger.debug("error on pageid({}), marking \"FRONTIER\" and inserting status code".format(page.id))
        db.update_page(page.id, "FRONTIER", "", response.status_code, "", access)
        return

    # handle redirect
    # redirect pages are marked "HTML" but have no html content and one of redirect status codes
    if response.status_code >= 300 and "Location" in response.headers:
        logger.debug("handling redirect on pageid({}) to URL {}".format(page.id, response.headers["Location"]))
        db.update_page(page.id, "HTML", "", response.status_code)
        frontier.insert_page(response.headers["Location"])
        return

    # content types reference:
    # https://www.iana.org/assignments/media-types/media-types.xhtml
    #
    # content types just for microsoft documents:
    # https://stackoverflow.com/a/4212908
    content_type = response.headers["Content-Type"]

    # handle document types
    page_type = "BINARY" # avoid repetition for page_type
    if content_type == "application/pdf":
        data_type = "PDF"
    elif content_type == "application/msword":
        data_type = "DOC"
    elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        data_type = "DOCX"
    elif content_type == "application/vnd.ms-powerpoint":
        data_type = "PPT"
    elif content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        data_type = "PPTX"
    else:
        page_type = None
    if page_type == "BINARY":
        logger.debug("pageid({}) is document of type \"{}\"".format(page.id, data_type))
        db.insert_page_data(page.id, data_type)
        db.update_page(page.id, "BINARY", "", response.status_code, "", access)
        return

    # handle image types
    if content_type.startswith("image/"):
        # if image URLs are not recognized by their extensions, then this
        # name can be awkward
        filename = page.url.split("/")[-1]
        # "Date" header parsing explained: https://stackoverflow.com/a/59416334
        accessed = parsedate_to_datetime(response.headers["Date"])
        logger.debug("pageid({}) is image of type \"{}\" and filename \"{}\"".format(page.id, content_type, filename))
        db.insert_image_data(page.id, filename, content_type, accessed)
        db.update_page(page.id, "BINARY", "", response.status_code, "", access)
        return

    if "text/html" not in content_type:
        # What to do with types other than specified documents, images or HTML?
        # How should such pages be marked?
        # Or should such pages be deleted from database?
        #
        # For now, leave page type and html empty and insert status code.
        # Frontier will not pick up such pages.
        logger.debug("pageid({}) is of no useful format".format(page.id))
        db.update_page(page.id, "", "", response.status_code, "", access)
        return

    # handle HTML content
    logger.debug("pageid({}) is HTML, waiting on siteid({})".format(page.id, page.siteid))
    scheduler.wait_site(page.siteid)
    # selenium should be used here
    response = requests.get(page.url, headers=headers)
    access = datetime.datetime.now()
    logger.debug("sent GET request to pageid({}) at URL {}".format(page.id, page.url))

    # this fail is weird since we managed to fetch headers previously; save for later
    if response.status_code >= 400:
        logger.debug("unexpected error on pageid({}), marking \"FRONTIER\" and inserting status code".format(page.id))
        db.update_page(page.id, "FRONTIER", "", response.status_code, "", access)
        return
    text = response.text

    hash = create_content_hash(text)
    if hash:
        dupid = db.hash_duplicate_check(hash)
        if dupid:
            logger.debug("pageid({}) is duplicate of pageid({})".format(page.id, dupid))
            db.update_page(page.id, "DUPLICATE", "", response.status_code, "", access)
            db.insert_link(page.id, dupid)
            return
    else:
        hash = ""

    #logger.debug("HTML on pageid({}) {}".format(page.id, text))
    links = get_links(page.url, text)
    images = get_images(page.url, text)

    logger.debug("pageid({}) is HTML, marking \"HTML\"".format(page.id))
    db.update_page(page.id, "HTML", text, response.status_code, hash, access)

    for url in links:
        logger.debug("inserting new URL {}".format(url))
        new_pageid = frontier.insert_page(url)
        # new page can fail to be inserted for two reasons:
        # - it is not allowed (robots.txt filters) or
        # - it is already in page table (db constraint)
        #
        # in second case we still need to add link between pages
        # so we need to get the id of existing page
        if new_pageid:
            logger.debug("inserting link from pageid({}) to pageid({})".format(page.id, new_pageid))
            db.insert_link(page.id, new_pageid)
        else:
            existing_id = db.get_page_with_url(url)
            if existing_id:
                logger.debug("inserting link from pageid({}) to pageid({})".format(page.id, existing_id))
                db.insert_link(page.id, existing_id)
    for url in images:
        logger.debug("inserting new image at {}".format(url))
        frontier.insert_page(url)


def create_content_hash(html_content):
    try:
        m = hashlib.sha256()
        m.update(html_content.encode('utf-8'))
        return m.hexdigest()
    except Exception as e:
        logger.debug(str(e))
        return None


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


def get_links(url, text):
    """Scan the text for http URLs and return a set
    of URLs found, without duplicates"""

    # look for any http URL in the page
    links = set()

    soup = BeautifulSoup(text, features="html.parser")
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
        text = get_page(url)
        links = get_links(url, text)
        urls.update(links)
        # add the url back to the set
        urls.add(url)

    return urls


def get_images(url, text):
    """Scan the text for images and return a set
    of images, without duplicates"""

    # look for any http URL in the page
    images = set()

    soup = BeautifulSoup(text, features="html.parser")
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