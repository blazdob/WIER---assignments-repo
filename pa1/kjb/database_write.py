
def write_site_to_db(conn, domain, robots_content, sitemap_content):
    cur = conn.cursor()
    try:
        sql = "UPDATE crawldb.site SET robots_content = %s,sitemap_content=%s WHERE domain=%s"
        cur.execute(sql, (robots_content, sitemap_content, domain))
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        cur.close()

def write_pg_data_to_db(conn, pg_id, data_type_code, data):
    cur = conn.cursor()

    sql = 'INSERT INTO crawldb.pg_data (page_id, data_type_code, data) ' \
          'VALUES (%s,%s,%s)'
    try:
        cur.execute(sql, (pg_id, data_type_code, data))
        conn.commit()
        cur.close()
    except Exception:
        conn.rollback()
        cur.close()


def write_img_to_db(conn, imgs_data, url):
    for img in imgs_data:
        cur = conn.cursor()
        sql = 'INSERT INTO crawldb.image (page_id, filename, content_type, data, accessed_time) ' \
              'VALUES ((SELECT id from crawldb.page WHERE url=%s), %s, %s, %s , %s )'
        try:
            cur.execute(sql, (url, img[0], img[1], img[2], img[3], ))
            conn.commit()
            cur.close()
        except Exception as e:
            conn.rollback()
            cur.close()
