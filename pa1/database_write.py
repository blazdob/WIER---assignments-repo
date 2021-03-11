
def write_url_to_db(conn, links, page_index):
    return 0

def write_site_to_db(conn, domain, robots_content, sitemap_content):
    cur = conn.cursor()
    try:
        sql = "UPDATE crawldb.site SET robots_content = %s,sitemap_content=%s WHERE domain=%s"
        cur.execute(sql, (robots_content, sitemap_content, domain))
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        conn.commit()
        cur.close()

def write_page_data_to_db(conn, page_id, data_type_code, data):
    cur = conn.cursor()

    sql = 'INSERT INTO crawldb.page_data (page_id, data_type_code,data) ' \
          'VALUES (%s,%s,%s)'
    try:
        cur.execute(sql, (page_id, data_type_code, data))
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        conn.commit()
        cur.close()


def write_image_to_db(conn, page_id, filename, content_type, data, accessed_time):
    return 0