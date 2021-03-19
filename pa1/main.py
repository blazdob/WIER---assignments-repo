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
from kjb.crawler import crawl_page


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
    frontier.insert_page("https://evem.gov.si")
    frontier.insert_page("https://e-uprava.gov.si")
    frontier.insert_page("https://e-prostor.gov.si")
    logger.debug("done bootstrapping frontier")


def pages_exist_thread(frontier, scheduler, db):
    logger.debug("thread started")
    while True:
        page = frontier.get_next_page()
        if not page:
            logger.debug("no page, thread done")
            return
        crawl_page(frontier, scheduler, page, db)


def oneshot_thread(frontier, scheduler, db):
    logger.debug("thread started")
    page = frontier.get_next_page()
    if not page:
        logger.debug("no page, thread done")
        return
    crawl_page(frontier, scheduler, page, db)
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


def test_single_threaded(frontier, scheduler, db):
    bootstrap_frontier(frontier)

    page = frontier.get_next_page()
    while page:
        crawl_page(frontier, scheduler, page, db)
        page = frontier.get_next_page()

    logger.debug("done processing pages")


def test_pages_exist_threading(frontier, scheduler, db):
    bootstrap_frontier(frontier)

    while True:
        logger.debug("starting threads")
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            for _ in range(WORKERS):
                executor.submit(pages_exist_thread, frontier, scheduler, db)
        logger.debug("all pages have been processed, sleeping for 5 seconds ...")
        time.sleep(5)


def test_batch_threading(frontier, scheduler, db):
    bootstrap_frontier(frontier)

    while True:
        logger.debug("starting threads")
        with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
            for _ in range(WORKERS):
                executor.submit(oneshot_thread, frontier, scheduler, db)
        logger.debug("page batch processed, sleeping 5 seconds ...")
        time.sleep(5)


def test_config():
    logger.debug("DB_HOST: \"{}\"".format(kjb.config.DB_HOST))
    logger.debug("DB_PORT: \"{}\"".format(kjb.config.DB_PORT))
    logger.debug("DB_DB: \"{}\"".format(kjb.config.DB_DB))
    logger.debug("DB_USER: \"{}\"".format(kjb.config.DB_USER))
    logger.debug("DB_PASS: \"{}\"".format(kjb.config.DB_PASS))

    logger.debug("USER_AGENT: \"{}\"".format(kjb.config.USER_AGENT))
    logger.debug("DRIVER_CHROME: \"{}\"".format(kjb.config.DRIVER_CHROME))
    logger.debug("DEFAULT_DELAY: \"{}\"".format(kjb.config.DEFAULT_DELAY))
    logger.debug("AGENT_RULES: \"{}\"".format(kjb.config.AGENT_RULES))


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

    #test_single_threaded(frontier, scheduler, db)
    #test_pages_exist_threading(frontier, scheduler, db)
    test_batch_threading(frontier, scheduler, db)

    conn.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        quit = True