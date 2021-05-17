import os
import sqlite3
from pathlib import Path
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.treebank import TreebankWordDetokenizer


stop_words_slovene = set(stopwords.words("slovene")).union(set(
        ["ter","nov","novo", "nova","zato","še", "zaradi", "a", "ali", "april", "avgust", "b", "bi", "bil", "bila", "bile", "bili", "bilo", "biti",
         "blizu", "bo", "bodo", "bojo", "bolj", "bom", "bomo", "boste", "bova", "boš", "brez", "c", "cel", "cela",
         "celi", "celo", "d", "da", "daleč", "dan", "danes", "datum", "december", "deset", "deseta", "deseti", "deseto",
         "devet", "deveta", "deveti", "deveto", "do", "dober", "dobra", "dobri", "dobro", "dokler", "dol", "dolg",
         "dolga", "dolgi", "dovolj", "drug", "druga", "drugi", "drugo", "dva", "dve", "e", "eden", "en", "ena", "ene",
         "eni", "enkrat", "eno", "etc.", "f", "februar", "g", "g.", "ga", "ga.", "gor", "gospa", "gospod", "h", "halo",
         "i", "idr.", "ii", "iii", "in", "iv", "ix", "iz", "j", "januar", "jaz", "je", "ji", "jih", "jim", "jo",
         "julij", "junij", "jutri", "k", "kadarkoli", "kaj", "kajti", "kako", "kakor", "kamor", "kamorkoli", "kar",
         "karkoli", "katerikoli", "kdaj", "kdo", "kdorkoli", "ker", "ki", "kje", "kjer", "kjerkoli", "ko", "koder",
         "koderkoli", "koga", "komu", "kot", "kratek", "kratka", "kratke", "kratki", "l", "lahka", "lahke", "lahki",
         "lahko", "le", "lep", "lepa", "lepe", "lepi", "lepo", "leto", "m", "maj", "majhen", "majhna", "majhni",
         "malce", "malo", "manj", "marec", "me", "med", "medtem", "mene", "mesec", "mi", "midva", "midve", "mnogo",
         "moj", "moja", "moje", "mora", "morajo", "moram", "moramo", "morate", "moraš", "morem", "mu", "n", "na", "nad",
         "naj", "najina", "najino", "najmanj", "naju", "največ", "nam", "narobe", "nas", "nato", "nazaj", "naš", "naša",
         "naše", "ne", "nedavno", "nedelja", "nek", "neka", "nekaj", "nekatere", "nekateri", "nekatero", "nekdo",
         "neke", "nekega", "neki", "nekje", "neko", "nekoga", "nekoč", "ni", "nikamor", "nikdar", "nikjer", "nikoli",
         "nič", "nje", "njega", "njegov", "njegova", "njegovo", "njej", "njemu", "njen", "njena", "njeno", "nji",
         "njih", "njihov", "njihova", "njihovo", "njiju", "njim", "njo", "njun", "njuna", "njuno", "no", "nocoj",
         "november", "npr.", "o", "ob", "oba", "obe", "oboje", "od", "odprt", "odprta", "odprti", "okoli", "oktober",
         "on", "onadva", "one", "oni", "onidve", "osem", "osma", "osmi", "osmo", "oz.", "p", "pa", "pet", "peta",
         "petek", "peti", "peto", "po", "pod", "pogosto", "poleg", "poln", "polna", "polni", "polno", "ponavadi",
         "ponedeljek", "ponovno", "potem", "povsod", "pozdravljen", "pozdravljeni", "prav", "prava", "prave", "pravi",
         "pravo", "prazen", "prazna", "prazno", "prbl.", "precej", "pred", "prej", "preko", "pri", "pribl.",
         "približno", "primer", "pripravljen", "pripravljena", "pripravljeni", "proti", "prva", "prvi", "prvo", "r",
         "ravno", "redko", "res", "reč", "s", "saj", "sam", "sama", "same", "sami", "samo", "se", "sebe", "sebi",
         "sedaj", "sedem", "sedma", "sedmi", "sedmo", "sem", "september", "seveda", "si", "sicer", "skoraj", "skozi",
         "slab", "smo", "so", "sobota", "spet", "sreda", "srednja", "srednji", "sta", "ste", "stran", "stvar", "sva",
         "t", "ta", "tak", "taka", "take", "taki", "tako", "takoj", "tam", "te", "tebe", "tebi", "tega", "težak",
         "težka", "težki", "težko", "ti", "tista", "tiste", "tisti", "tisto", "tj.", "tja", "to", "toda", "torek",
         "tretja", "tretje", "tretji", "tri", "tu", "tudi", "tukaj", "tvoj", "tvoja", "tvoje", "u", "v", "vaju", "vam",
         "vas", "vaš", "vaša", "vaše", "ve", "vedno", "velik", "velika", "veliki", "veliko", "vendar", "ves", "več",
         "vi", "vidva", "vii", "viii", "visok", "visoka", "visoke", "visoki", "vsa", "vsaj", "vsak", "vsaka", "vsakdo",
         "vsake", "vsaki", "vsakomur", "vse", "vsega", "vsi", "vso", "včasih", "včeraj", "x", "z", "za", "zadaj",
         "zadnji", "zakaj", "zaprta", "zaprti", "zaprto", "zdaj", "zelo", "zunaj", "č", "če", "često", "četrta",
         "četrtek", "četrti", "četrto", "čez", "čigav", "š", "šest", "šesta", "šesti", "šesto", "štiri", "ž", "že",
         "svoj", "jesti", "imeti","\u0161e", "iti", "kak", "www", "km", "eur", "pač", "del", "kljub", "šele", "prek",
         "preko", "znova", "morda","kateri","katero","katera", "ampak", "lahek", "lahka", "lahko", "morati", "torej"]))

DOCUMENT_FOLDER = os.path.join(os.pardir, "documents")
INDEX_FILENAME = "inverted-index.db"
NUM_RESULTS = 3
NEIGHBORHOOD = 3


def preprocess(text):
    """Returns a list of tuples including a word and its index in document."""
    text_words = word_tokenize(text)
    words = []
    ix = 0
    for rawWord in text_words:
        lowerWord = rawWord.lower()
        if lowerWord not in stop_words_slovene:
            words.append((lowerWord, ix))
        ix += 1
    return words


# generator function
def documents():
    """Returns tuples of document name and relative file path."""
    for domain in os.listdir(DOCUMENT_FOLDER):
        for docname in os.listdir(os.path.join(DOCUMENT_FOLDER, domain)):
            filename = os.path.join(DOCUMENT_FOLDER, domain, docname)
            if filename.endswith(".html"):
                fullDocname = os.path.join(domain, docname)
                yield (fullDocname, filename)


# A posting entry is a key string of a word and a value dictionary with
# a frequency integer and a list of indexes.
def process_document(text):
    """Returns a dictionary of postings."""
    words = preprocess(text)
    postings = {}
    for word, ix in words:
        if word in postings:
            wordinfo = postings[word]
        else:
            wordinfo = {"frequency": 0, "indexes": []}
            postings[word] = wordinfo
        wordinfo["frequency"] += 1
        wordinfo["indexes"].append(ix)
    return postings


def write_postings(docname, postings, dbcon):
    """Writes a dictionary of postings to database."""
    cur = dbcon.cursor()
    for word, posting in postings.items():
        # generate text of indexes
        indexes = ""
        for ix in posting["indexes"]:
            indexes += "{},".format(ix)
        indexes = indexes.rstrip(",")
        # insert into database; nested try is needed to handle rollback
        # and commit properly
        try:
            try:
                cur.execute("INSERT INTO IndexWord VALUES (?)", (word,))
            except sqlite3.IntegrityError: # word already in index
                pass
            cur.execute(
                "INSERT INTO Posting VALUES (?, ?, ?, ?)",
                (word, docname, posting["frequency"], indexes)
            )
        except Exception as e:
            print(e)
            dbcon.rollback()
        else:
            dbcon.commit()


def create_tables(dbcon):
    cur = dbcon.cursor()
    cur.execute("""
        CREATE TABLE IndexWord (
            word TEXT PRIMARY KEY
        )
    """)

    cur.execute("""
        CREATE TABLE Posting (
            word TEXT NOT NULL,
            documentName TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            indexes TEXT NOT NULL,
            PRIMARY KEY(word, documentName),
            FOREIGN KEY (word) REFERENCES IndexWord(word)
        )
    """)
    dbcon.commit()


def delete_tables(dbcon):
    cur = dbcon.cursor()
    cur.execute("DROP TABLE IF EXISTS IndexWord")
    cur.execute("DROP TABLE IF EXISTS Posting")
    dbcon.commit()


def connect_database():
    return sqlite3.connect(INDEX_FILENAME)


def extract_snippets(tokenized_words, indexes):
    """Returns a string of snippets around words at given indexes."""
    # First, convert a list of indexes to a list of tuples that
    # represent ranges from which snippets should be built.
    # This is done to merge snippets whose indexes overlap
    # with another snippet's neighborhood
    ranges = []
    i = 0
    while i < len(indexes):
        rangeStart = indexes[i]
        rangeStop = indexes[i]

        # swallow the next n indexes into range that are less
        # than neighborhood away one from another
        j = i + 1
        if j < len(indexes):
            while abs(indexes[j] - rangeStop) < NEIGHBORHOOD + 1:
                rangeStop = indexes[j]
                j += 1
                if j == len(indexes):
                    break
        ranges.append((rangeStart, rangeStop))
        i = j

    # Build snippets from ranges
    snippets = ""
    for rangeStart, rangeStop in ranges:
        startix = rangeStart - NEIGHBORHOOD
        if startix < 0:
            startix = 0
        stopix = rangeStop + NEIGHBORHOOD + 1
        snippet_tokens = tokenized_words[startix:stopix]
        # Detokenization: https://stackoverflow.com/a/41305584
        snippets += "{} ... ".format(TreebankWordDetokenizer().detokenize(snippet_tokens))
    return snippets


def print_results_header():
    print("{0:<11} {1:<50} {2:<60}".format("Frequencies", "Document", "Snippet"))
    print("{0:-<11} {1:-<50} {2:-<60}".format("", "", ""))


def print_results(results, number=-1):
    count = 0
    for doc in results:
        print("{0:<11} {1:<50} {2:<60}".format(
            doc["frequency"],
            doc["name"],
            doc["snippets"]
        ))
        count += 1
        if count == number:
            return