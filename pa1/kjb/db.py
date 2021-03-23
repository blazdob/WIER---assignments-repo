import logging
import threading
import psycopg2


logger = logging.getLogger(__name__)


class DB(object):

    _conn = None
    _lock = threading.Lock()

    def __init__(self, conn):
        DB._conn = conn
    
    # TODO: sitemap is empty until strategy for handling it is determined
    def insert_or_update_site(self, domain, robots=""):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                # check if site already exists
                cur.execute("SELECT 1 FROM crawldb.site WHERE domain = %s", (domain,))
                if cur.fetchone(): # site exists, update it
                    cur.execute("UPDATE crawldb.site SET robots_content = %s WHERE domain = %s RETURNING id", (robots, domain))
                else: # doesn't exist, insert
                    cur.execute("INSERT INTO crawldb.site (domain, robots_content, sitemap_content) VALUES (%s,%s,%s) RETURNING id", (domain, robots, ""))
            except psycopg2.Error as e:
                logger.error(str(e))
                DB._conn.rollback()
            else:
                DB._conn.commit()
                return cur.fetchone()[0] # return id
            finally:
                cur.close()

    def get_sites(self):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute("SELECT * FROM crawldb.site")
            except psycopg2.Error as e:
                logger.error(str(e))
            else:
                return cur.fetchall()
            finally:
                cur.close()

    def insert_page(self, url, siteid, timestamp):
        """
        Insert page with given URL to database.

        Expects properly processed URL. Other page data is going to be
        updated later when crawler picks it up from frontier.
        """
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute("INSERT INTO crawldb.page (site_id, url, accessed_time) VALUES (%s,%s,%s) RETURNING id", (siteid, url, timestamp))
            except psycopg2.Error as e:
                logger.debug(str(e))
                DB._conn.rollback()
            else:
                DB._conn.commit()
                return cur.fetchone()[0]
            finally:
                cur.close()

    def get_unprocessed_pages(self):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute("SELECT id, site_id, url FROM crawldb.page WHERE html_content is NULL AND http_status_code IS NULL ORDER BY accessed_time")
            except psycopg2.Error as e:
                logger.error(str(e))
            else:
                return cur.fetchall()
            finally:
                cur.close()

    def update_page(self, id, type, html, http_status, hash, timestamp):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute("UPDATE crawldb.page SET page_type_code = %s, html_content = %s, http_status_code = %s, html_hash = %s, accessed_time = %s WHERE id = %s", (type, html, http_status, hash, timestamp, id))
            except psycopg2.Error as e:
                logger.debug(str(e))
                DB._conn.rollback()
            else:
                DB._conn.commit()
            finally:
                cur.close()

    def insert_page_data(self, pageid, data_type):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute('INSERT INTO crawldb.page_data (page_id, data_type_code) VALUES (%s,%s)', (pageid, data_type))
            except psycopg2.Error as e:
                logger.error(str(e))
                DB._conn.rollback()
            else:
                DB._conn.commit()
            finally:
                cur.close()

    def insert_image_data(self, pageid, filename, content_type, accessed):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute('INSERT INTO crawldb.image (page_id, filename, content_type, accessed_time) VALUES (%s,%s,%s,%s)', (pageid, filename, content_type, accessed))
            except psycopg2.Error as e:
                logger.debug(str(e))
                DB._conn.rollback()
            else:
                DB._conn.commit()
            finally:
                cur.close()

    def insert_link(self, from_page, to_page):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute('INSERT INTO crawldb.link (from_page, to_page) VALUES (%s,%s)', (from_page, to_page))
            except psycopg2.Error as e:
                logger.error(str(e))
                DB._conn.rollback()
            else:
                DB._conn.commit()
            finally:
                cur.close()

    def get_page_with_url(self, url):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute("SELECT id FROM crawldb.page WHERE url = %s", (url,))
            except psycopg2.Error as e:
                logger.error(str(e))
            else:
                row = cur.fetchone()
                if row:
                    return row[0]
            finally:
                cur.close()


    def hash_duplicate_check(self, hash):
        with DB._lock:
            try:
                cur = DB._conn.cursor()
                cur.execute("SELECT id FROM crawldb.page WHERE html_hash=%s", (hash,))
            except Exception as e:
                logger.error(str(e))
            else:
                row = cur.fetchone()
                if row:
                    return row[0]
            finally:
                cur.close()