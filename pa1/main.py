import psycopg2
import threading
import datetime
import logging
import time
import concurrent.futures

from kjb.config import parse_config, DB_HOST, DB_PORT, DB_DB, DB_USER, DB_PASS
from kjb.db import DB
from kjb.frontier import Frontier


WORKERS = 4
logger = logging.getLogger(__name__)


def bootstrap_frontier(db, frontier):
    if not db.get_sites():
        logger.debug("bootstrapping frontier")
        f.insert_page("https://gov.si")
        f.insert_page("https://evem.gov.si")
        f.insert_page("https://e-uprava.gov.si")
        f.insert_page("https://e-prostor.gov.si")
        sites = db.get_sites()
        logger.debug("showing sites directly from DB: {}".format(str(sites)))


def simple_thread(frontier):
    logger.debug("thread started")
    while True:
        logger.debug("getting page from frontier")
        url, delay = frontier.get_next_page()
        if not url:
            logger.debug("no url, finishing".format(delay))
            return

        logger.debug("url from frontier: {}".format(url))
        logger.debug("waiting {} seconds".format(delay))
        time.sleep(delay)
        logger.debug("waiting done")


def test_schema(conn):
    cur = conn.cursor()
    print("Databases:")
    cur.execute("SELECT datname FROM pg_database;")
    print(cur.fetchall())
    print()
    print()
    print("Tables in crawldb schema:")
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'crawldb';")
    tables = [result[0] for result in cur.fetchall()]
    for table in tables:
        print(table)
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name =%s;", (table,))
        print(cur.fetchall())
        print()
    cur.close()


def test_get_sites(db):
    rows = db.get_sites()
    print(rows)
    print(type(rows[0][0]))
    print(type(rows[0][1]))
    print(type(rows[0][2]))
    print(type(rows[0][3]))


def test_get_unprocessed_pages(db):
    rows = db.get_unprocessed_pages()
    print(rows)
    print(rows[0])
    print(type(rows[0][0]))


def test_frontier(db):
    f = Frontier(db)
    bootstrap_frontier(db, f)
    f.initialize()
    logger.debug("frontier initialized")

    url, delay = f.get_next_page()
    while url:
        logger.debug("url from frontier: {}".format(url))
        logger.debug("waiting {} seconds".format(delay))
        time.sleep(delay)
        logger.debug("waiting done")
        url, delay = f.get_next_page()

    logger.debug("done processing pages")


def test_frontier_threading(db):
    f = Frontier(db)
    bootstrap_frontier(db, f)
    f.initialize()
    logger.debug("frontier initialized")

    while True:
        logger.debug("starting threads")
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            for _ in range(WORKERS):
                executor.submit(simple_thread, f)
        logger.debug("all pages have been processed, sleeping for 5 seconds ...")
        time.sleep(5)


def main():
    logging.basicConfig(format="thread(%(thread)d): %(levelname)s: %(module)s: %(funcName)s: %(message)s", level=logging.DEBUG)
    parse_config()

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DB,
        user=DB_USER,
        password=DB_PASS
    )

    db = DB(conn)

    test_frontier_threading(db)

    conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit = True