# Notes:
# - robots.txt files don't get refreshed. What would the proper
#   implementation be (out of scope of this project probably, just
#   good to include in report)?

import threading
import requests
import logging
import time
import datetime
import collections

from urllib.parse import urlparse, urljoin, urldefrag
from reppy.robots import Robots
from url_normalize import url_normalize
from requests.exceptions import RequestException


USER_AGENT = "fri-wier-kjb"
AGENT_RULES = "*"
HEADERS = {"User-agent":USER_AGENT}
FETCH_DELAY = 5
EMPTY_DELAY = 1
logger = logging.getLogger(__name__)


class Frontier(object):

    _db = None
    _lock = threading.Lock()
    _hosts = {}
    _queue = collections.deque()

    def __init__(self, db):
        Frontier._db = db

    def _canonicalize_url(self, url):
        # canonicalization transformations that don't work as per lecture 4 slide 16:
        # - guessed directory
        # - default filename
        url = url_normalize(url)
        url, _ = urldefrag(url)
        return url

    def initialize(self):
        with Frontier._lock:
            # fill _hosts
            rows = Frontier._db.get_sites()
            for row in rows:
                site = Site(row[1])
                site.update_access()
                site.id = row[0]
                site.robotstr = row[2]
                site.sitemap = row[3]
                site.parse_robots()
                Frontier._hosts[row[1]] = site

            # fill _queue
            Frontier._queue.clear()
            rows = Frontier._db.get_unprocessed_pages()
            for row in rows:
                Frontier._queue.appendleft(row[0])
    
    def insert_page(self, url):
        with Frontier._lock:
            url = self._canonicalize_url(url)
            domain = urlparse(url).netloc
            if domain not in Frontier._hosts: # create site
                site = Site(domain)
                site.fetch_robots()
                site.parse_robots()
                site.update_db_site(Frontier._db)
                Frontier._hosts[domain] = site
            
            site = Frontier._hosts[domain]
            if not site.agent.allowed(url):
                logger.debug("given URL is not allowed")
                return
            Frontier._db.insert_page(url, site.id, datetime.datetime.now())
            try:
                Frontier._queue.index(url)
            except ValueError: # url is not yet in queue
                Frontier._queue.appendleft(url)
            else:
                logger.debug("URL already in frontier")

    def get_next_page(self):
        with Frontier._lock:
            if not len(Frontier._queue):
                return None, EMPTY_DELAY
            url = Frontier._queue.pop()
            domain = urlparse(url).netloc
            site = Frontier._hosts[domain]
            diff = datetime.datetime.now() - site.last_access
            delta = datetime.timedelta(days=0, seconds=site.delay)
            if diff > delta:
                delay = 0
            else:
                delay = (delta - diff).seconds
            site.update_access()
            return url, delay


class Site(object):

    def __init__(self, domain):
        self._domain = domain
        self._parser = None
        self._robots_url = ""

        self.id = None
        self.robotstr = ""
        self.sitemap = ""
        self.delay = FETCH_DELAY
        # not really now, but has to be something
        self.last_access = datetime.datetime.now()
        self.agent = None

    def fetch_robots(self):
        url = urljoin("https://"+self._domain, "robots.txt")
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                self.robotstr = response.text
                self._robots_url = url
        except RequestException as e:
            logger.debug("error with retrieving robots.txt: {}".format(str(e)))
        finally:
            self.update_access()

    def parse_robots(self):
        self._parser = Robots.parse(self._robots_url, self.robotstr)
        self.agent = self._parser.agent(AGENT_RULES)
        self.delay = self.agent.delay
        if not self.delay:
            self.delay = FETCH_DELAY

    def update_db_site(self, db):
        self.id = db.insert_or_update_site(self._domain, self.robotstr)
    
    def update_access(self):
        self.last_access = datetime.datetime.now()