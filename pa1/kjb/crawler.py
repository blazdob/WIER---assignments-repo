import urllib.request
import time
import re
import logging
import requests
import hashlib
import datetime

from selenium.common.exceptions import WebDriverException
from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
from email.utils import parsedate_to_datetime
from requests.exceptions import RequestException

from . import config


REGEX = "^(?:https?:\/\/)?(?:[^\.]+\.)?gov\.si(\/.*)?$"

TAGS = ['a', 'link']

headers = {'User-Agent': config.USER_AGENT}
logger = logging.getLogger(__name__)


def crawl_page(frontier, scheduler, page, db, driver):
    logger.info("crawling on pageid({}) at {} on siteid({})".format(page.id, page.url, page.siteid))

    # fetch head
    logger.debug("waiting on siteid({})".format(page.siteid))
    scheduler.wait_site(page.siteid)

    try:
        response = requests.head(page.url, headers=headers)
    except RequestException as e:
        logger.info("error fetching headers: {}".format(str(e)))
        db.update_page(page.id, "ERROR", None, None, None, datetime.datetime.now())
        return

    access = datetime.datetime.now()
    logger.debug("sent HEAD request to pageid({}) at URL {}".format(page.id, page.url))

    # mark error
    if response.status_code >= 400:
        logger.info("error on HEAD request on pageid({})".format(page.id))
        db.update_page(page.id, "ERROR", None, response.status_code, None, access)
        return

    # handle and mark redirect
    if response.status_code >= 300:
        logger.info("redirect on pageid({})".format(page.id))
        db.update_page(page.id, "REDIRECT", None, response.status_code, None, access)
        targetid = frontier.insert_page(response.headers.get("Location", ""))
        if targetid:
            db.insert_link(page.id, targetid)
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
        logger.info("pageid({}) is document of type \"{}\"".format(page.id, data_type))
        db.insert_page_data(page.id, data_type)
        db.update_page(page.id, "BINARY", None, response.status_code, None, access)
        return

    # handle image types
    if content_type.startswith("image/"):
        # if image URLs are not recognized by their extensions, then this
        # name can be awkward
        filename = page.url.split("/")[-1]
        # "Date" header parsing explained: https://stackoverflow.com/a/59416334
        accessed = parsedate_to_datetime(response.headers["Date"])
        logger.info("pageid({}) is image of type \"{}\" and filename \"{}\"".format(page.id, content_type, filename))
        db.insert_image_data(page.id, filename, content_type, accessed)
        db.update_page(page.id, "BINARY", None, response.status_code, None, access)
        return

    # mark such pages as "OTHER"
    if "text/html" not in content_type:
        logger.info("pageid({}) is of no useful format".format(page.id))
        db.update_page(page.id, "OTHER", None, response.status_code, None, access)
        return

    # handle HTML content
    logger.debug("pageid({}) is HTML, waiting on siteid({})".format(page.id, page.siteid))
    scheduler.wait_site(page.siteid)

    # fetch page with selenium
    try:
        driver.get(page.url)
        time.sleep(config.SELENIUM_DELAY)
        text = driver.page_source
    except WebDriverException as e:
        logger.info("error fetching HTML content: {}".format(str(e)))
        db.update_page(page.id, "ERROR", None, None, None, datetime.datetime.now())
        return

    access = datetime.datetime.now()
    logger.debug("selenium get pageid({}) at URL {}".format(page.id, page.url))

    # check duplicate
    hash = create_content_hash(text)
    if hash:
        dupid = db.hash_duplicate_check(hash)
        if dupid:
            logger.info("pageid({}) is duplicate of pageid({})".format(page.id, dupid))
            db.update_page(page.id, "DUPLICATE", None, response.status_code, None, access)
            db.insert_link(page.id, dupid)
            return
    else:
        hash = ""

    # update page record in database
    db.update_page(page.id, "HTML", text, response.status_code, hash, access)

    # process links and urls in HTML
    links = get_links(page.url, text)
    images = get_images(page.url, text)
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
        logger.error(str(e))
        return None


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