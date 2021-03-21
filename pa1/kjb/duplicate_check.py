import hashlib

def create_content_hash(html_content):
    try:
        m = hashlib.sha256()
        m.update(html_content.encode('utf-8'))
        return m.hexdigest()
    except Exception as error:
        print("ERROR while creating hash: ", error)
        return None

def hash_duplicate_check(hash, conn):
    try:
        cur = conn.cursor()
        cur.execute(
            """
                SELECT * FROM crawldb.page WHERE hash_content=%s;
            """, (hash,) )
        conn.commit()
        page = cur.fetchone()
        return page is not None
    except Exception as error:
        print("ERROR when duplicating: ", error)

