import psycopg2
import threading
import datetime
import logging
import time
import concurrent.futures
import kjb.config

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from kjb.db import DB
from kjb.frontier import Frontier
from kjb.scheduler import Scheduler
from kjb.crawler import crawl_page


logger = logging.getLogger(__name__)


def create_webdrivers():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent={}".format(kjb.config.USER_AGENT))

    webdrivers = []
    for _ in range(kjb.config.WORKERS):
        if not kjb.config.DRIVER_LOCATION:
            driver = webdriver.Chrome(options=chrome_options)
        else:
            driver = webdriver.Chrome(kjb.config.DRIVER_LOCATION, options=chrome_options)
        webdrivers.append(driver)
    return webdrivers


def create_db_front_and_sched(conn):
    db = DB(conn)
    logger.info("database initialized")
    s = Scheduler(db)
    s.initialize()
    logger.info("scheduler initialized")
    f = Frontier(db, s)
    f.initialize()
    logger.info("frontier initialized")
    return db, f, s


def bootstrap_frontier(frontier, db):
    if not db.get_sites():
        logger.info("frontier is empty, bootstrapping with seed pages")
        frontier.insert_page("https://gov.si")
        frontier.insert_page("https://evem.gov.si")
        frontier.insert_page("https://e-uprava.gov.si")
        frontier.insert_page("https://e-prostor.gov.si")
        logger.info("done bootstrapping frontier")


def oneshot_thread(frontier, scheduler, db, webdriver):
    logger.debug("thread started")
    page = frontier.get_next_page()
    if not page:
        logger.debug("no page, thread done")
        return
    crawl_page(frontier, scheduler, page, db, webdriver)
    logger.debug("thread done")


def oneshot_thread_with_page(frontier, scheduler, page, db, webdriver):
    logger.debug("thread started")
    crawl_page(frontier, scheduler, page, db, webdriver)
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


def crawl_BFS(frontier, scheduler, db, webdrivers):
    while True:
        try:
            if kjb.config.WORKERS > 1:
                logger.info("starting threads")
                with concurrent.futures.ThreadPoolExecutor(max_workers=kjb.config.WORKERS) as executor:
                    for i in range(kjb.config.WORKERS):
                        executor.submit(oneshot_thread, frontier, scheduler, db, webdrivers[i])
            else:
                oneshot_thread(frontier, scheduler, db, webdrivers[0])

            logger.info("page batch processed, sleeping {} seconds ...".format(kjb.config.BATCH_DELAY))
            time.sleep(kjb.config.BATCH_DELAY)
        except KeyboardInterrupt:
            return


def crawl_by_site_access(frontier, scheduler, db, webdrivers):
    while True:
        try:
            logger.info("getting pages by site")
            Frontier._queue.clear() # frontier's queue is not needed in this strategy
            pages = frontier.get_pages_by_site(list(Scheduler._sites_by_id.values()), kjb.config.WORKERS)
            if kjb.config.WORKERS > 1:
                logger.info("starting threads")
                with concurrent.futures.ThreadPoolExecutor(max_workers=kjb.config.WORKERS) as executor:
                    for i in range(kjb.config.WORKERS):
                        if i >= len(pages):
                            break
                        executor.submit(oneshot_thread_with_page, frontier, scheduler, pages[i], db, webdrivers[i])
            else:
                oneshot_thread_with_page(frontier, scheduler, pages[0], db, webdrivers[0])

            logger.info("page batch processed, sleeping {} seconds ...".format(kjb.config.BATCH_DELAY))
            time.sleep(kjb.config.BATCH_DELAY)
        except KeyboardInterrupt:
            return


def test_config():
    logger.critical("DB_HOST: {}".format(kjb.config.DB_HOST))
    logger.critical("DB_PORT: {}".format(kjb.config.DB_PORT))
    logger.critical("DB_DB: {}".format(kjb.config.DB_DB))
    logger.critical("DB_USER: {}".format(kjb.config.DB_USER))
    logger.critical("DB_PASS: {}".format(kjb.config.DB_PASS))

    logger.critical("USER_AGENT: {}".format(kjb.config.USER_AGENT))
    logger.critical("DRIVER_LOCATION: {}".format(kjb.config.DRIVER_LOCATION))
    logger.critical("DEFAULT_DELAY: {}".format(kjb.config.DEFAULT_DELAY))
    logger.critical("AGENT_RULES: {}".format(kjb.config.AGENT_RULES))
    logger.critical("SELENIUM_DELAY: {}".format(kjb.config.SELENIUM_DELAY))

    logger.critical("WORKERS: {}".format(kjb.config.WORKERS))
    logger.critical("BATCH_DELAY: {}".format(kjb.config.BATCH_DELAY))

    # for log level integer meaning: https://docs.python.org/3.8/library/logging.html#logging-levels
    logger.critical("LOG_LEVEL: {}".format(kjb.config.LOG_LEVEL))
    logger.critical("STRATEGY: {}".format(kjb.config.STRATEGY))


def main():
    kjb.config.parse_config()
    kjb.config.parse_arguments()
    logging.basicConfig(format="%(asctime)s: thread(%(thread)d): %(levelname)s: %(module)s: %(funcName)s: %(message)s", level=kjb.config.LOG_LEVEL)

    #test_config()
    #return

    conn = psycopg2.connect(
        host=kjb.config.DB_HOST,
        port=kjb.config.DB_PORT,
        database=kjb.config.DB_DB,
        user=kjb.config.DB_USER,
        password=kjb.config.DB_PASS
    )

    db, frontier, scheduler = create_db_front_and_sched(conn)
    bootstrap_frontier(frontier, db)
    webdrivers = create_webdrivers()

    if kjb.config.STRATEGY == "BATCH_BFS":
        crawl_BFS(frontier, scheduler, db, webdrivers)
    else:
        crawl_by_site_access(frontier, scheduler, db, webdrivers)

    for driver in webdrivers:
        driver.quit()

    conn.close()


if __name__ == "__main__":
    main()