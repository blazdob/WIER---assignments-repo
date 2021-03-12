# Notes:
# - robots.txt files don't get refreshed. What would the proper
#   implementation be (out of scope of this project probably, just
#   good to include in report)?

import threading
import requests
import logging
import time
import datetime
from urllib.parse import urlparse, urljoin


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
    
    def insert_page(self, url):
        """
        Expects canonized and non duplicate URL.
        """
        with _lock:
            domain = urlparse(url).netloc
            if domain not in _hosts:
                # check if URL works
                response = requests.head(url, headers=HEADERS)
                if response.status_code >= 400:
                    logging.debug("frontier: insert_page: error with given page URL")
                    return
                time.sleep(DELAY) # sleep default delay

                # create site
                site = Site(domain)
                self._hosts[domain] = site
                site.fetch_robots()
                site.parse_robots()
                site.update_db_site(_db)
            
            # TODO: check against disallowed and allowed statements
            _db.insert_page(url)


class Site(object):

    def __init__(self, domain):
        self.id = None
        self.domain = domain
        self.robotstr = ""
        self.sitemap = ""

        self.delay = DELAY
        self.allowed = []
        self.disallowed = []
        self.last_access = None
    
    def fetch_robots(self):
        url = urljoin(self.domain, "robots.txt")
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return
        self.robotstr = response.text
        self.update_access()

    def parse_robots(self):
        parseRules = False
        for line in self.robotstr:
            sline = line.strip() # strip whitespace from both ends
            if not sline and parseRules: # blank line, end of record, done parsing
                break
            elif not sline or sline[0] == "#": # blank line or comment, ignore
                continue
            elif "user-agent" in sline.lower(): # user-agent line
                agent = sline.split()[-1]
                if agent == AGENT_RULES:
                    parseRules = True
            elif parseRules:
                value = sline.split()[-1]
                if sline.startswith("Allow"):
                    self.allowed.append(value)
                elif sline.startswith("Disallow"):
                    self.disallowed.append(value)
                elif sline.startswith("Crawl-delay"):
                    self.delay = int(value)

    def update_db_site(self, db):
        self.id = db.insert_or_update_site(self.domain, self.robotstr, self.sitemap)
    
    def update_access(self):
        self.last_access = datetime.datetime.now()