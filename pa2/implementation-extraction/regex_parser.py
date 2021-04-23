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

siol = [ '../input-extraction/Bravo ne izstopa le v Sloveniji, ampak tudi Evropi - siol.net.html',
         '../input-extraction/Novi kodiaq na cesti ga bo težko ločiti od starega #foto - siol.net.html'
]

cleaner = Cleaner()

def regex_parser(html_code, page_source):

    for page in rtv_slo:
        tmp = read_page(page)
        tmp2 = parse_rtv(tmp)


    for page in over_stock:
        tmp = read_page(page)
        tmp2 = parse_overstock(tmp)


    for page in siol:
        tmp = read_page(page)
        tmp2 = parse_siol(tmp)

    return 0


def read_page(page_path):
    return codecs.open(page_path, encoding='utf-8', errors='replace').read()


def parse_rtv(page):

    page = cleaner.clean_html(page)

    regex = r"<div class=\"author-name\">(.*)</div>"
    match = re.compile(regex).search(page)
    author = match.group(1)

    regex = r"<div class=\"publish-meta\">(.*?)<br>"
    match = re.search(regex, page, re.DOTALL)
    date = match.group(1)
    date = ' '.join(date.split())

    regex = r"<h1>(.*)<\/h1>"
    match = re.compile(regex).search(page)
    title = match.group(1)

    regex = r"<div class=\"subtitle\">(.*)</div>"
    match = re.compile(regex).search(page)
    subtitle = match.group(1)

    regex = r"<p class=\"lead\">(.*)</p>"
    match = re.compile(regex).search(page)
    abstract = match.group(1)

    regex = r"<article class=\"article\">(.*?)<\/article>"
    match = re.search(regex, page, re.DOTALL)
    content = match.group(1)
    content2 = ' '.join(content.split())
    content3 = re.sub(r"<[^>]*>", "", content2)

    return (
        json.dumps(
            {
                "Author": author,
                "Date": date,
                "Title": title,
                "SubTitle": subtitle,
                "Abstract": abstract,
                "Content": content3
            },
            ensure_ascii=False)
    )

def parse_overstock(page):
    productId = 0
    products = []

    regex = r"<b>([0-9]+-(.+)(?=\</b>))</b>"
    titles = []
    matches = re.finditer(regex, page)
    for match in matches:
        titles.append(match.group(1))

    regex = r"<s>(.*?)</s>"
    lastPrices = []
    matches = re.finditer(regex, page)
    for match in matches:
        lastPrices.append(match.group(1))


    regex = r"<b>([$€]\s*[0-9\.,]+)</b>"
    prices = []
    matches = re.finditer(regex, page)
    for match in matches:
        prices.append(match.group(1))


    regex = r"\(([0-9]+%\))"
    percents = []
    matches = re.finditer(regex, page)
    for match in matches:
        percents.append(match.group(0))


    regex = r"([$€]\s*[0-9\.,]+ )"
    savings = []
    matches = re.finditer(regex, page)
    for match in matches:
        savings.append(match.group(1).strip())


    regex = r"<td valign=\"top\"><span class=\"normal\">(.*?)<\/b>"
    descriptions = []
    matches = re.finditer(regex, page, re.DOTALL)
    for match in matches:
        con = match.group(1)
        con2 = ' '.join(con.split())
        con3 = re.sub(r"<[^>]*>", "", con2)
        descriptions.append(con3)

    dolzina = len(titles)

    while dolzina >= productId:
        # print(titles[0])
        try:
            title = titles[productId]
            lastPrice = lastPrices[productId]
            price = prices[productId]
            saving = savings[productId]
            savingPercent = percents[productId]
            description = descriptions[productId]
            products.append(
                {
                    "ListPrice": lastPrice,
                    "Price": price,
                    "Saving": saving,
                    "SavingPercent": savingPercent,
                    "Title": title,
                    "Content": description
                }
            )
        except:
            pass

        productId = productId + 1

    return json.dumps([ob for ob in products])

def parse_siol(page):
    page = cleaner.clean_html(page)

    regex = r"<\s*h1[^>]*>(.*?)<\s*/\s*h1>"
    match = re.compile(regex).search(page)
    title = match.group(1)


    regex = r"<a href=\"/avtorji/(.*)>(.*)"
    match = re.compile(regex).search(page)
    con = match.group(2)
    author = re.sub(r'[^. š A-Za-z0-9]+', '', match.group(2))


    regex = r"<span class=\"article__publish_date--date\">(.*?)</span>"
    match = re.search(regex, page, re.DOTALL)
    con = match.group(1).replace("\n", "").replace(";", "")
    date = re.sub(r'[^.A-Za-z0-9]+', '', con)


    regex = r"<div class=\"article__intro js_articleIntro\">(.*?)</div>"
    match = re.search(regex, page, re.DOTALL)
    first = match.group(1)
    content3 = re.sub(r"<[^>]*>", "", first)
    abstract = re.sub(r'[^. šŠčČžŽA-Za-z0-9]+', '', content3)


    regex = r"<div class=\"article__main js_article js_bannerInArticleWrap\">(.*?)</div>"
    match = re.search(regex, page, re.DOTALL)
    first = match.group(1)
    con = re.sub(r"<[^>]*>", "", first)
    content = re.sub(r'[^. šŠčČžŽA-Za-z0-9]+', '', con)

    return (
        json.dumps(
            {
                "Author": author,
                "PublishedTime": date,
                "Title": title,
                "Abstract": abstract,
                "Content": content
            },
            ensure_ascii=False)
    )