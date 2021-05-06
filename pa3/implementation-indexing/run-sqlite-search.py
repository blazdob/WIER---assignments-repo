import os
import sys
import datetime
from bs4 import BeautifulSoup
from nltk import word_tokenize
from processing import DOCUMENT_FOLDER, extract_snippets, preprocess, \
    print_results_header, print_results, connect_database

def find_documents(query_words, dbcon):
    cur = dbcon.cursor()

    # create (?, ?, ?, ...) for all query words
    template_str = ""
    for word in query_words:
        template_str += "?,"
    template_str = template_str.rstrip(",")

    cur.execute("SELECT * FROM Posting WHERE word IN ({})".format(template_str), query_words)

    # result_documents is a dictionary of entries with document name as key and
    # frequency, snippets and tokenized word list in a dictionary as a value
    result_documents = {}
    for posting in cur.fetchall():
        docname = posting[1]
        if docname in result_documents: # take existing doc entry
            doc = result_documents[docname]
        else: # create new doc entry; have to read document and tokenize
            filename = os.path.join(DOCUMENT_FOLDER, docname)
            with open(filename, "r", encoding="utf8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                text = soup.get_text()
                toktext = word_tokenize(text)
                doc = {
                    "frequency": 0,
                    "snippets": " ... ",
                    "toktext": toktext,
                    "name": docname
                }
                result_documents[docname] = doc
        # update doc entry
        doc["frequency"] += posting[2]
        indexes = [int(ix) for ix in posting[3].split(",")]
        doc["snippets"] += extract_snippets(doc["toktext"], indexes)

    return result_documents.values()


def main():
    if len(sys.argv) != 2: # expecting single argument
        print("usage: python run-basic-search.py SEARCH_PARAM")
        sys.exit(1)

    # preprocess query; if no words remain, exit with error
    query = sys.argv[1]
    query_words = [result[0] for result in preprocess(query)]
    if not query_words:
        print("error: only stopwords included in query \"{}\"".format(query))
        sys.exit(1)

    print("Results for a query: \"{}\"".format(query))
    print() # blank line

    startT = datetime.datetime.now()

    dbcon = connect_database()

    result_documents = find_documents(query_words, dbcon)
    result_documents = sorted( # sort documents by frequency
        result_documents,
        key=lambda doc: doc["frequency"],
        reverse=True
    )

    dbcon.close()

    delta = datetime.datetime.now() - startT

    print("Results found in: {}".format(delta))
    print() # blank line

    print_results_header()
    print_results(result_documents)


if __name__ == "__main__":
    #import cProfile
    #pr = cProfile.Profile()
    #pr.enable()
    main()
    #pr.disable()
    #pr.print_stats(sort="cumtime")