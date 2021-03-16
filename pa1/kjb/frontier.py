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
from reppy.robots import Robots


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
                site.parse_robots()
                site.update_db_site(_db)
            
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
        response = requests.get(url, headers=HEADERS)
        self.update_access()
        if response.status_code != 200:
            return
        self._robotstr = response.text
        self._parser = Robots.parse(url, self._robotstr)
        self.agent = self._parser.agent(AGENT_RULES)
        self.delay = agent.delay
        if not self.delay:
            self.delay = DELAY

        #parseRules = False
        #for line in self._robotstr:
        #    sline = line.strip() # strip whitespace from both ends
        #    if not sline and parseRules: # blank line, end of record, done parsing
        #        break
        #    elif not sline or sline[0] == "#": # blank line or comment, ignore
        #        continue
        #    elif "user-agent" in sline.lower(): # user-agent line
        #        agent = sline.split()[-1]
        #        if agent == AGENT_RULES:
        #            parseRules = True
        #    elif parseRules:
        #        value = sline.split()[-1]
        #        if sline.startswith("Allow"):
        #            self.allowed.append(value)
        #        elif sline.startswith("Disallow"):
        #            self.disallowed.append(value)
        #        elif sline.startswith("Crawl-delay"):
        #            self.delay = int(value)

    def update_db_site(self, db):
        self._id = db.insert_or_update_site(self._domain, self._robotstr)
    
    def update_access(self):
        self.last_access = datetime.datetime.now()