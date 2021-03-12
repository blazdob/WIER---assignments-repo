import configparser


DB_HOST = "localhost"
DB_PORT = 5432
DB_DB   = "postgres"
DB_USER = "user"
DB_PASS = "password"


def parse_config():
    global DB_HOST, DB_PORT, DB_DB, DB_USER, DB_PASS # needed to modify
    config = configparser.ConfigParser()
    config.read("config.ini")
    if "database" in config:
        DB_HOST = config["database"].get("host", DB_HOST)
        DB_PORT = config["database"].get("port", DB_PORT)
        DB_DB   = config["database"].get("database", DB_DB)
        DB_USER = config["database"].get("user", DB_USER)
        DB_PASS = config["database"].get("password", DB_PASS)