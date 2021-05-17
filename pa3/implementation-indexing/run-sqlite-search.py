import os
import sys
import datetime
from bs4 import BeautifulSoup
from nltk import word_tokenize
from processing import DOCUMENT_FOLDER, extract_snippets, preprocess, \
    print_results_header, print_results, connect_database, NUM_RESULTS

def find_documents(query_words, dbcon):
    cur = dbcon.cursor()

    # create (?, ?, ?, ...) for all query words
    template_str = ""
    for word in query_words:
        template_str += "?,"
    template_str = template_str.rstrip(",")

    cur.execute("SELECT * FROM Posting WHERE word IN ({})".format(template_str), query_words)

    # result_documents is a dictionary of entries with document name as key and
    # frequency, document name (needed later) and indexes in a dictionary as a value
    result_documents = {}
    for posting in cur.fetchall():
        docname = posting[1]
        if docname in result_documents: # take existing doc entry
            doc = result_documents[docname]
        else: # create new doc entry
            doc = {
                "frequency": 0,
                "indexes": [],
                "name": docname
            }
            result_documents[docname] = doc
        # update doc entry
        doc["frequency"] += posting[2]
        indexes = [int(ix) for ix in posting[3].split(",")]
        doc["indexes"].extend(indexes)

    # sort documents by frequency
    sorted_documents = sorted(
        result_documents.values(),
        key=lambda doc: doc["frequency"],
        reverse=True
    )

    # extract snippets from documents and add them to doc dicts
    top_documents = sorted_documents[:NUM_RESULTS]
    for doc in top_documents:
        filename = os.path.join(DOCUMENT_FOLDER, doc["name"])
        with open(filename, "r", encoding="utf8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            text = soup.get_text()
            toktext = word_tokenize(text)
            doc["snippets"] = " ... "
            doc["snippets"] += extract_snippets(toktext, doc["indexes"])

    return top_documents


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