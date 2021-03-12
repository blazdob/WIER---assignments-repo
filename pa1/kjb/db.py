class DB(object):

    _conn = None
    _lock = None

    def __init__(self, conn, lock):
        _conn = conn
        _lock = lock
    
    # TODO: sitemap is empty until strategy for handling it is determined
    def insert_or_update_site(self, domain, robots=""):
        with _lock:
            try:
                cur = _conn.cursor()
                # check if site already exists
                cur.execute("SELECT 1 FROM crawldb.site WHERE domain = %s", (domain,))
                if cur.fetchone(): # site exists, update it
                    cur.execute("UPDATE crawldb.site SET robots_content = %s WHERE domain = %s RETURNING id", (robots, domain))
                else: # doesn't exist, insert
                    cur.execute("INSERT INTO crawldb.site VALUES (%s,%s,%s) RETURNING id", (domain, robots, ""))
            except:
                _conn.rollback()
            else:
                _conn.commit()
                return cur.fetchone() # return id
            finally:
                cur.close()
    
    def insert_page(self, url):
        """
        Insert page with given URL to database.

        Expects properly processed URL. Other page data is going to be
        updated later when crawler picks it up from frontier.
        """
        with _lock:
            try:
                cur = _conn.cursor()
                cur.execute("INSERT INTO crawldb.page (url) VALUES (%s)", (url,))
            except:
                _conn.rollback()
            else:
                _conn.commit()
            finally:
                cur.close()