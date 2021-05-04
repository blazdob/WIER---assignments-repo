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
        tmp = prepare_page(page)
        #tmp2 = parse_rtv(tmp)
        print(parse_rtv(tmp))


    for page in over_stock:
        tmp = prepare_page(page)
        #tmp2 = parse_overstock(tmp)
        print(parse_overstock(tmp))


    for page in siol:
        tmp = prepare_page(page)
        #tmp2 = parse_siol(tmp)
        print(parse_siol(tmp))

        #print(tmp2)

    return 0


def prepare_page(page_path):
    page = codecs.open(page_path, encoding='utf-8', errors='replace').read()
    return cleaner.clean_html(page)


def parse_rtv(page):

    #Author - RTV
    regex = r"<div class=\"author-name\">(.*)</div>"
    match = re.compile(regex).search(page)
    author = match.group(1)

    #Title - RTV
    regex = r"<h1>(.*)<\/h1>"
    match = re.compile(regex).search(page)
    title = match.group(1)

    #Subtitle - RTV
    regex = r"<div class=\"subtitle\">(.*)</div>"
    match = re.compile(regex).search(page)
    subtitle = match.group(1)

    #Date - RTV
    regex = r"<div class=\"publish-meta\">(.*?)<br>"
    match = re.search(regex, page, re.DOTALL)
    date = match.group(1)
    date = ' '.join(date.split())

    #Lead - RTV
    regex = r"<p class=\"lead\">(.*)</p>"
    match = re.compile(regex).search(page)
    abstract = match.group(1)

    #Content - RTV
    regex = r"<article class=\"article\">(.*?)<\/article>"
    match = re.search(regex, page, re.DOTALL)
    first = ' '.join(match.group(1).split())
    content = re.sub(r"<[^>]*>", "", first)
    #print(content)

    return (
        json.dumps(
            {
                "Author": author,
                "Date": date,
                "Title": title,
                "SubTitle": subtitle,
                "Abstract": abstract,
                "Content": content
            },
            ensure_ascii=False)
    )

def parse_overstock(page):
    prodId = 0
    prdcts = []

    #Title - Overstock
    regex = r"<b>([0-9]+-(.+)(?=\</b>))</b>"
    titles = []
    matches = re.finditer(regex, page)
    for match in matches:
        titles.append(match.group(1))

    #LastPrices - Overstock
    regex = r"<s>(.*?)</s>"
    listPrices = []
    matches = re.finditer(regex, page)
    for match in matches:
        listPrices.append(match.group(1))

    #Prices - Overstock
    regex = r"<b>([$€]\s*[0-9\.,]+)</b>"
    prices = []
    matches = re.finditer(regex, page)
    for match in matches:
        prices.append(match.group(1))

    # Content - OverStock
    regex = r"<td valign=\"top\"><span class=\"normal\">(.*?)<\/b>"
    contents = []
    matches = re.finditer(regex, page, re.DOTALL)
    for match in matches:
        content = ' '.join(match.group(1).split())
        final = re.sub(r"<[^>]*>", "", content)
        contents.append(final)

    #Percents - Overstock
    regex = r"\(([0-9]+%\))"
    percents = []
    matches = re.finditer(regex, page)
    for match in matches:
        percents.append(match.group(0))

    #Savings - Overstock
    regex = r"([$€]\s*[0-9\.,]+ )"
    savings = []
    matches = re.finditer(regex, page)
    for match in matches:
        savings.append(match.group(1).strip())

    while len(titles) >= prodId:
        try:
            prdcts.append(
                {
                    "ListPrice": listPrices[prodId],
                    "Price": prices[prodId],
                    "Saving": savings[prodId],
                    "SavingPercent": percents[prodId],
                    "Title": titles[prodId],
                    "Content": contents[prodId]
                },
            )
        except:
            pass

        prodId = prodId + 1

    return json.dumps([dump for dump in prdcts])


def parse_siol(page):

    #Title - Siol
    regex = r"<\s*h1[^>]*>(.*?)<\s*/\s*h1>"
    match = re.compile(regex).search(page)
    title = match.group(1)

    #Author - Siol
    regex = r"<a href=\"/avtorji/(.*)>(.*)"
    match = re.compile(regex).search(page)
    author = re.sub(r'[^. š A-Za-z0-9]+', '', match.group(2))

    #Date - Siol
    regex = r"<span class=\"article__publish_date--date\">(.*?)</span>"
    match = re.search(regex, page, re.DOTALL)
    con = match.group(1).replace("\n", "").replace(";", "")
    date = re.sub(r'[^.A-Za-z0-9]+', '', con)

    #Intro - Siol
    regex = r"<div class=\"article__intro js_articleIntro\">(.*?)</div>"
    match = re.search(regex, page, re.DOTALL)
    first = match.group(1)
    content3 = re.sub(r"<[^>]*>", "", first)
    intro = re.sub(r'[^. šŠčČžŽA-Za-z0-9]+', "", content3)

    #Content - Siol
    regex = r"<div class=\"article__main js_article js_bannerInArticleWrap\">(.*?)</div>"
    match = re.search(regex, page, re.DOTALL)
    first = match.group(1)
    con = re.sub(r"<[^>]*>", "", first)
    content = re.sub(r'[^. šŠčČžŽA-Za-z0-9]+', "", con)
    #print(content)

    return (
        json.dumps(
            {
                "Author": author,
                "PublishedTime": date,
                "Title": title,
                "Intro": intro,
                "Content": content
            },
            ensure_ascii=False)
    )