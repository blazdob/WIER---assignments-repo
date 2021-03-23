import configparser


DB_HOST = "localhost"
DB_PORT = 5432
DB_DB   = "postgres"
DB_USER = "postgres"
DB_PASS = "password"

USER_AGENT = "fri-wier-KJB"
DRIVER_CHROME = "" # if empty, default is used
DEFAULT_DELAY = 5
AGENT_RULES = "*"
WORKERS = 4


def parse_config():
    global DB_HOST, DB_PORT, DB_DB, DB_USER, DB_PASS # needed to modify
    global USER_AGENT, DRIVER_CHROME, DEFAULT_DELAY, AGENT_RULES
    global WORKERS
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
        DRIVER_CHROME = config["crawler"].get("driver_chrome", DRIVER_CHROME)
        DEFAULT_DELAY = int(config["crawler"].get("default_delay", DEFAULT_DELAY))
        AGENT_RULES = config["crawler"].get("agent_rules", AGENT_RULES)
        WORKERS = int(config["crawler"].get("workers", WORKERS))