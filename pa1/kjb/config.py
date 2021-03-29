import configparser
import logging


DB_HOST = "localhost"
DB_PORT = 5432
DB_DB   = "postgres"
DB_USER = "user"
DB_PASS = "password"

USER_AGENT = "fri-wier-KJB"
DRIVER_LOCATION = "" # if empty, default is used
DEFAULT_DELAY = 5
AGENT_RULES = "*"
SELENIUM_DELAY = 5

WORKERS = 4
BATCH_DELAY = 2

LOG_LEVEL = logging.INFO


def translate_log_level(levelstr):
    if not levelstr:
        return logging.NOTSET
    if levelstr == "CRITICAL":
        return logging.CRITICAL
    elif levelstr == "ERROR":
        return logging.ERROR
    elif levelstr == "WARNING":
        return logging.WARNING
    elif levelstr == "INFO":
        return logging.INFO
    elif levelstr == "DEBUG":
        return logging.DEBUG
    else:
        return logging.NOTSET


def parse_config():
    # variables need to be declared global to be changed globally
    global DB_HOST, DB_PORT, DB_DB, DB_USER, DB_PASS
    global USER_AGENT, DRIVER_LOCATION, DEFAULT_DELAY, AGENT_RULES, SELENIUM_DELAY
    global WORKERS, BATCH_DELAY
    global LOG_LEVEL

    config = configparser.ConfigParser()
    config.read("config.ini")
    if "database" in config:
        DB_HOST = config["database"].get("host", DB_HOST)
        DB_PORT = int(config["database"].get("port", DB_PORT))
        DB_DB   = config["database"].get("database", DB_DB)
        DB_USER = config["database"].get("user", DB_USER)
        DB_PASS = config["database"].get("password", DB_PASS)

    if "crawler" in config:
        USER_AGENT = config["crawler"].get("user_agent", USER_AGENT)
        DRIVER_LOCATION = config["crawler"].get("driver_location", DRIVER_LOCATION)
        DEFAULT_DELAY = int(config["crawler"].get("default_delay", DEFAULT_DELAY))
        AGENT_RULES = config["crawler"].get("agent_rules", AGENT_RULES)
        SELENIUM_DELAY = int(config["crawler"].get("selenium_delay", SELENIUM_DELAY))

    if "threading" in config:
        WORKERS = int(config["threading"].get("workers", WORKERS))
        BATCH_DELAY = int(config["threading"].get("batch_delay", BATCH_DELAY))

    if "main" in config:
        LOG_LEVEL = translate_log_level(config["main"].get("log_level", "INFO"))