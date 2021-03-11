import psycopg2
import configparser


DB_HOST = "localhost"
DB_PORT = 5432
DB_DB   = "postgres"
DB_USER = "user"
DB_PASS = "password"


def parseConfig():
    global DB_HOST, DB_PORT, DB_DB, DB_USER, DB_PASS # needed to modify
    config = configparser.ConfigParser()
    config.read("config.ini")
    if "database" in config:
        DB_HOST = config["database"].get("host", DB_HOST)
        DB_PORT = config["database"].get("port", DB_PORT)
        DB_DB   = config["database"].get("database", DB_DB)
        DB_USER = config["database"].get("user", DB_USER)
        DB_PASS = config["database"].get("password", DB_PASS)


def main():
    parseConfig()

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DB,
        user=DB_USER,
        password=DB_PASS
    )
    conn.autocommit = True
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
    conn.close()


if __name__ == "__main__":
    main()