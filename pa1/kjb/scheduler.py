import threading
import requests
import logging
import time
import datetime

from urllib.parse import urljoin
from reppy.robots import Robots
from requests.exceptions import RequestException

from . import crawler
from . import config


logger = logging.getLogger(__name__)


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