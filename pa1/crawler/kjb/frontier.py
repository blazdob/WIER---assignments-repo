import threading
import logging
import datetime
import collections

from urllib.parse import urlparse, urldefrag
from url_normalize import url_normalize


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
                page = Page(row[0], row[1], row[2])
                Frontier._queue.appendleft(page)
    
    def insert_page(self, url):
        with Frontier._lock:
            url = self._canonicalize_url(url)
            domain = urlparse(url).netloc
            if not domain:
                logger.debug("could not parse domain")
                return None
            siteid = Frontier._scheduler.get_siteid(domain)
            
            if not Frontier._scheduler.site_allowed(siteid, url):
                logger.debug("given URL is not allowed")
                return None
            pageid = Frontier._db.insert_page(url, siteid, datetime.datetime.now())
            if pageid:
                page = Page(pageid, siteid, url)
                Frontier._queue.appendleft(page)
                return pageid
            else:
                logger.debug("URL already in page table")
                return None

    def get_next_page(self):
        with Frontier._lock:
            if not len(Frontier._queue):
                return None
            return Frontier._queue.pop()

    def get_pages_by_site(self, sites, num_pages):
        if not sites:
            return []

        # sort a list of sites by last access
        sites.sort(key=lambda site: site._last_access)

        # get a list of page lists from every site
        list_of_page_lists = []
        for site in sites:
            rows = Frontier._db.get_unprocessed_pages_by_site(site.id, num_pages)
            if not rows:
                continue
            site_pages = []
            for row in rows:
                site_pages.append(Page(row[0], row[1], row[2]))
            list_of_page_lists.append(site_pages)

        if not list_of_page_lists:
            return []

        pages = []
        for i in range(num_pages):
            for page_list in list_of_page_lists:
                if i >= len(page_list):
                    continue
                pages.append(page_list[i])
        return pages


class Page(object):

    def __init__(self, pageid, siteid, url):
        self.id = pageid
        self.siteid = siteid
        self.url = url