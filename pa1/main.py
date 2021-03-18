import psycopg2
import threading
import datetime
import logging
import time
import concurrent.futures
import kjb.config

from kjb.db import DB
from kjb.frontier import Frontier
from kjb.scheduler import Scheduler


WORKERS = 4
logger = logging.getLogger(__name__)


def create_db_front_and_sched(conn):
    db = DB(conn)
    logger.debug("database initialized")
    s = Scheduler(db)
    s.initialize()
    logger.debug("scheduler initialized")
    f = Frontier(db, s)
    f.initialize()
    logger.debug("frontier initialized")
    return db, f, s


def bootstrap_frontier(frontier):
    frontier.insert_page("https://gov.si")
    frontier.insert_page("https://www.gov.si/podrocja/")
    frontier.insert_page("https://www.gov.si/drzavni-organi/")
    frontier.insert_page("https://www.gov.si/zbirke/")
    frontier.insert_page("https://www.gov.si/dogodki/")
    frontier.insert_page("https://www.gov.si/novice/")
    frontier.insert_page("https://evem.gov.si")
    frontier.insert_page("https://e-uprava.gov.si")
    frontier.insert_page("https://e-prostor.gov.si")
    logger.debug("done bootstrapping frontier")


def pages_exist_thread(frontier, scheduler):
    logger.debug("thread started")
    while True:
        logger.debug("getting page from frontier")
        page = frontier.get_next_page()
        if not page:
            logger.debug("no page, thread done")
            return
        logger.debug("url from frontier: {}".format(page.url))
        logger.debug("waiting for site ...")
        scheduler.wait_site(page.siteid)
        logger.debug("waiting done")


def oneshot_thread(frontier, scheduler):
    logger.debug("thread started")
    logger.debug("getting page from frontier")
    page = frontier.get_next_page()
    if not page:
        logger.debug("no page, thread done")
        return
    logger.debug("url from frontier: {}".format(page.url))
    logger.debug("waiting for site ...")
    scheduler.wait_site(page.siteid)
    logger.debug("waiting done")
    logger.debug("thread done")


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


def test_frontier(frontier, scheduler):
    bootstrap_frontier(frontier)

    page = frontier.get_next_page()
    while page:
        logger.debug("url from frontier: {}".format(page.url))
        logger.debug("waiting for site ...")
        scheduler.wait_site(page.siteid)
        logger.debug("waiting done")
        page = frontier.get_next_page()

    logger.debug("done processing pages")


def test_frontier_threading(frontier, scheduler):
    bootstrap_frontier(frontier)

    while True:
        logger.debug("starting threads")
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            for _ in range(WORKERS):
                executor.submit(pages_exist_thread, frontier, scheduler)
        logger.debug("all pages have been processed, sleeping for 5 seconds ...")
        time.sleep(5)


def test_batch_threading(frontier, scheduler):
    bootstrap_frontier(frontier)

    while True:
        logger.debug("starting threads")
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            for _ in range(WORKERS):
                executor.submit(oneshot_thread, frontier, scheduler)
        logger.debug("page batch processed, sleeping 5 seconds ...")
        time.sleep(5)

def main():
    logging.basicConfig(format="%(asctime)s: thread(%(thread)d): %(levelname)s: %(module)s: %(funcName)s: %(message)s", level=logging.DEBUG)
    kjb.config.parse_config()

    conn = psycopg2.connect(
        host=kjb.config.DB_HOST,
        port=kjb.config.DB_PORT,
        database=kjb.config.DB_DB,
        user=kjb.config.DB_USER,
        password=kjb.config.DB_PASS
    )

    db, frontier, scheduler = create_db_front_and_sched(conn)

    #test_frontier(frontier, scheduler)
    #test_frontier_threading(frontier, scheduler)
    test_batch_threading(frontier, scheduler)

    conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit = True