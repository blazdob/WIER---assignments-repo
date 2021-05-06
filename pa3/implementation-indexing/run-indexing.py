from bs4 import BeautifulSoup
from processing import \
    connect_database, create_tables, delete_tables, documents, \
    process_document, write_postings


def main():
    dbcon = connect_database()

    delete_tables(dbcon)
    create_tables(dbcon)

    for docname, filename in documents():
        print("procesing document {} ...".format(docname))
        with open(filename, "r", encoding="utf8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            postings = process_document(soup.get_text())
            #print(postings)
            write_postings(docname, postings, dbcon)

    dbcon.close()


if __name__ == "__main__":
    main()