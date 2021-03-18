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

from . import crawler
from . import config


logger = logging.getLogger(__name__)


class Frontier(object):

    _db = None
    _scheduler = None
    _lock = threading.Lock()
    _queue = collections.deque()

    def __init__(self, db, scheduler):
        Frontier._db = db
        Frontier._scheduler = scheduler

    def _canonicalize_url(self, url):
        # canonicalization transformations that don't work as per lecture 4 slide 16:
        # - guessed directory
        # - default filename
        url = url_normalize(url)
        url, _ = urldefrag(url)
        return url

    def initialize(self):
        with Frontier._lock:
            Frontier._queue.clear()
            rows = Frontier._db.get_unprocessed_pages()
            for row in rows:
                Frontier._queue.appendleft(row[0])
    
    def insert_page(self, url):
        with Frontier._lock:
            url = self._canonicalize_url(url)
            domain = urlparse(url).netloc
            siteid = Frontier._scheduler.get_siteid(domain)
            
            if not Frontier._scheduler.site_allowed(siteid, url):
                logger.debug("given URL is not allowed")
                return
            Frontier._db.insert_page(url, siteid, datetime.datetime.now())
            try:
                Frontier._queue.index(url)
            except ValueError: # url is not yet in queue
                Frontier._queue.appendleft(url)
            else:
                logger.debug("URL already in frontier")

    def get_next_page(self):
        with Frontier._lock:
            if not len(Frontier._queue):
                return None, None
            url = Frontier._queue.pop()
            domain = urlparse(url).netloc
            return url, Frontier._scheduler.get_siteid(domain)


class Site(object):

    def __init__(self, domain):
        self._domain = domain
        self._parser = None
        self._robots_url = ""

        self.id = None
        self.robotstr = ""
        self.sitemap = ""
        self.delay = config.DEFAULT_DELAY
        # not really now, but has to be something
        self.last_access = datetime.datetime.now()
        self.agent = None
        self.lock = threading.Lock()

    def fetch_robots(self):
        url = urljoin("https://"+self._domain, "robots.txt")
        try:
            response = requests.get(url, headers=crawler.headers)
            if response.status_code == 200:
                self.robotstr = response.text
                self._robots_url = url
        except RequestException as e:
            logger.debug("error with retrieving robots.txt: {}".format(str(e)))
        finally:
            self.update_access()

    def parse_robots(self):
        self._parser = Robots.parse(self._robots_url, self.robotstr)
        self.agent = self._parser.agent(config.AGENT_RULES)
        self.delay = self.agent.delay
        if not self.delay:
            self.delay = config.DEFAULT_DELAY

    def update_db_site(self, db):
        self.id = db.insert_or_update_site(self._domain, self.robotstr)
    
    def update_access(self):
        self.last_access = datetime.datetime.now()


class Scheduler(object):

    _db = None
    _sites_by_domain = {}
    _sites_by_id = {}
    _lock = threading.Lock()

    def __init__(self, db):
        Scheduler._db = db

    def initialize(self):
        with Scheduler._lock:
            Scheduler._sites_by_domain = {}
            Scheduler._sites_by_id = {}
            rows = Scheduler._db.get_sites()
            for row in rows:
                site = Site(row[1])
                site.update_access()
                site.id = row[0]
                site.robotstr = row[2]
                site.sitemap = row[3]
                site.parse_robots()
                self._add_site(site, row[1])

    def _add_site(self, site, domain):
        Scheduler._sites_by_id[site.id] = site
        Scheduler._sites_by_domain[domain] = site

    def get_siteid(self, domain):
        with Scheduler._lock:
            if domain in Scheduler._sites_by_domain:
                return Scheduler._sites_by_domain[domain].id
            site = Site(domain)
            site.fetch_robots()
            site.parse_robots()
            site.update_db_site(Scheduler._db)
            self._add_site(site, domain)
            return site.id

    def site_allowed(self, siteid, url):
        return Scheduler._sites_by_id[siteid].agent.allowed(url)

    def wait_site(self, siteid):
        site = Scheduler._sites_by_id[siteid]
        with site.lock:
            diff = datetime.datetime.now() - site.last_access
            delta = datetime.timedelta(days=0, seconds=site.delay)
            if diff > delta:
                delay = 0
            else:
                delay = (delta - diff).seconds
            time.sleep(delay)
            site.update_access()