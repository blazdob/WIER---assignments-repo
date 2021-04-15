import re
import json
import codecs
from lxml.html.clean import Cleaner

rtv_slo = [
    '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html',
    '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html'
]

over_stock = [
    '../input-extraction/overstock.com/jewelry01.html',
    '../input-extraction/overstock.com/jewelry02.html'
]

cleaner = Cleaner()

def regex_parser(html_code, page_source):
<<<<<<< Updated upstream
    return 0

def rtv(page):
    return 0

def overstock(page):
    return 0

def tretja_stran(page):
    return 0
=======
    for page in rtv_slo:
        #pageContent = open(page, 'r').read()
        print(parse_rtv(read_page(page)))
        #print(parse_rtv(read_page(pageContent)))

def read_page(page_path):
    return codecs.open(page_path, encoding='utf-8', errors='replace').read()

def parse_rtv(page):

    page = cleaner.clean_html(page)
    # print(page)
    regex = r"<div class=\"author-name\">(.*)</div>"
    match = re.compile(regex).search(page)
    author = match.group(1)

    regex = r"<div class=\"publish-meta\">(.*?)<br>"
    match = re.search(regex, page, re.DOTALL)
    date = match.group(1)
    # date = re.sub('\s+', ' ', date)
    date = ' '.join(date.split())

    regex = r"<h1>(.*)<\/h1>"  # (.*)<\/h1>" #>\(.*)<\/div>"
    match = re.compile(regex).search(page)
    title = match.group(1)

    regex = r"<div class=\"subtitle\">(.*)</div>"  # >\(.*)<\/div>"
    match = re.compile(regex).search(page)
    subtitle = match.group(1)

    regex = r"<p class=\"lead\">(.*)</p>"  # >\(.*)<\/div>"
    match = re.compile(regex).search(page)
    lead = match.group(1)

    regex = r"<article class=\"article\">(.*?)<\/article>"
    match = re.search(regex, page, re.DOTALL)
    content = match.group(1)
    content2 = ' '.join(content.split())
    # content3 = content2.replace(r"<[^>]*>", "", content2)
    content3 = re.sub(r"<[^>]*>", "", content2)
    print("#########################", content2)
    # print(content3)
    return (
        json.dumps(
            {
                "Author": author,
                "PublishedTime": date,
                "Title": title,
                "SubTitle": subtitle,
                "Lead": lead,
                "Content": content3
            },
            ensure_ascii=False)
    )
>>>>>>> Stashed changes
