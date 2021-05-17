import sys
import datetime
from bs4 import BeautifulSoup
from nltk import word_tokenize
from processing import preprocess, process_document, documents, \
    extract_snippets, print_results_header, print_results, NUM_RESULTS


# result_documents is a list of dictionaries of document name, frequency sum
# and snippets
def find_documents(query_words):
    result_documents = []
    for docname, filename in documents(): # process all documents
        with open(filename, "r", encoding="utf8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            text = soup.get_text()
            tokenized_words = word_tokenize(text)
            postings = process_document(text)

            frequency = 0
            snippets = " ... "
            for word in query_words:
                if word in postings:
                    frequency += postings[word]["frequency"]
                    snippets += extract_snippets(tokenized_words, postings[word]["indexes"])

            if frequency > 0:
                result_documents.append({
                    "name": docname,
                    "frequency": frequency,
                    "snippets": snippets
                })

    return result_documents


def main():
    if len(sys.argv) != 2: # expecting one query argument
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

    result_documents = find_documents(query_words)
    result_documents = sorted(
        result_documents,
        key=lambda doc: doc["frequency"],
        reverse=True
    )

    delta = datetime.datetime.now() - startT

    print("Results found in: {}".format(delta))
    print() # blank line

    print_results_header()
    print_results(result_documents[:NUM_RESULTS])


if __name__ == "__main__":
    main()