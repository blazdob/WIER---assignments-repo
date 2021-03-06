import os
import sys

overstock1 = '../input-extraction/overstock.com/jewelry01.html'
overstock2 = '../input-extraction/overstock.com/jewelry02.html'
rtvslo1 = '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html'
rtvslo2 = '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html'
siol1 = '../input-extraction/Bravo ne izstopa le v Sloveniji, ampak tudi Evropi - siol.net.html'
siol2 = '../input-extraction/Novi kodiaq na cesti ga bo težko ločiti od starega #foto - siol.net.html'



page_source = overstock1  # rtvslo1, rtvslo2, overstock1, overstock2, ....., .......
#print(open(page_source))
SOURCE_NAME = "overstock1"

##### MAIN PROGRAM

#get HTML code
htmlObject = open(page_source, 'rb')
html_code = htmlObject.read()
#print(html_code)

# parsing the correct way
output = ""
try:
    if sys.argv[1] == "A":
        from regex_parser import regex_parser
        regex_parser(html_code, SOURCE_NAME)
    elif sys.argv[1] == "B":
        from xpath_parser import xpath_parser
        with open(overstock1, "r") as f:
            print(xpath_parser(f.read(), "overstock1"))
        with open(overstock2, "r") as f:
            print(xpath_parser(f.read(), "overstock2"))
        with open(rtvslo1, "r", encoding="utf-8") as f:
            print(xpath_parser(f.read(), "rtvslo1"))
        with open(rtvslo2, "r", encoding="utf-8") as f:
            print(xpath_parser(f.read(), "rtvslo2"))
        with open(siol2, "r", encoding="utf-8") as f:
            print(xpath_parser(f.read(), "siol1"))
        with open(siol2, "r", encoding="utf-8") as f:
            print(xpath_parser(f.read(), "siol2"))
        #output = xpath_parser(html_code, SOURCE_NAME)
    elif sys.argv[1] == "C":
        from roadrunner_parser import roadrunner_parser
        with open(overstock1, "r") as f1:
            with open(overstock2, "r") as f2:
                print(roadrunner_parser(f1.read(), f2.read()))
        with open(rtvslo1, "r", encoding="utf8") as f1:
            with open(rtvslo2, "r", encoding="utf8") as f2:
                print(roadrunner_parser(f1.read(), f2.read()))
        with open(siol1, "r", encoding="utf8") as f1:
            with open(siol2, "r", encoding="utf8") as f2:
                print(roadrunner_parser(f1.read(), f2.read()))
except Exception as error:
    print(error)

#print(output)
