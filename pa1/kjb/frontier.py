# Notes:
# - robots.txt files don't get refreshed. What would the proper
#   implementation be (out of scope of this project probably, just
#   good to include in report)?

import threading
import requests
import logging
import time
import datetime

from urllib.parse import urlparse, urljoin, urldefrag
from reppy.robots import Robots
from url_normalize import url_normalize


USER_AGENT = "fri-wier-kjb"
AGENT_RULES = "*"
HEADERS = {"User-agent":USER_AGENT}
DELAY = 5


class Frontier(object):

    _db = None
    _lock = threading.Lock()
    _hosts = {}

    def __init__(self, db):
        _db = db

    def _canonicalize_url(self, url):
        # canonicalization transformations that don't work as per lecture 4 slide 16:
        # - guessed directory
        # - default filename
        url = url_normalize(url)
        url, _ = urldefrag(url)
        return url
    
    def insert_page(self, url):
        with _lock:
            url = self._canonicalize_url(url)
            domain = urlparse(url).netloc
            if domain not in _hosts: # create site
                site = Site(domain)
                site.parse_robots()
                site.update_db_site(_db)
                self._hosts[domain] = site
            
            site = self._hosts[domain]
            if not site.agent.allowed(url):
                logging.debug("frontier: insert_page: given URL is not allowed")
                return
            _db.insert_page(url)


class Site(object):

    def __init__(self, domain):
        self._id = None
        self._domain = domain
        self._robotstr = ""
        self._sitemap = ""
        self._parser = None

        self.delay = DELAY
        self.last_access = None
        self.agent = None
    
    def parse_robots(self):
        url = urljoin(self._domain, "robots.txt")
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                self._robotstr = response.text
        except:
            logging.debug("frontier: parse_robots: error with retrieving robots.txt")
        finally:
            self.update_access()

        self._parser = Robots.parse(url, self._robotstr)
        self.agent = self._parser.agent(AGENT_RULES)
        self.delay = agent.delay
        if not self.delay:
            self.delay = DELAY

    def update_db_site(self, db):
        self._id = db.insert_or_update_site(self._domain, self._robotstr)
    
    def update_access(self):
        self.last_access = datetime.datetime.now()