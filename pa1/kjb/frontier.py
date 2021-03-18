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