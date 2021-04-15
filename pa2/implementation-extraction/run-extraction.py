import os
import numpy as np
import sys

overstock1 = '../input-extraction/overstock.com/jewelry01.html'
overstock2 = '../input-extraction/overstock.com/jewelry02.html'
rtvslo1 = '../input-extraction/rtvslo.si/Audi A6 50 TDI quattro_ nemir v premijskem razredu - RTVSLO.si.html'
rtvslo2 = '../input-extraction/rtvslo.si/Volvo XC 40 D4 AWD momentum_ suvereno med najboljše v razredu - RTVSLO.si.html'
####TODO PUT 2 MORE HTML WEBSITES



page_source = rtvslo1  # rtvslo1, rtvslo2, overstock1, overstock2, ....., .......
#print(open(page_source))


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
        output = regex_parser(html_code, page_source)
    elif sys.argv[1] == "B":
        from xpath_parser import xpath_parser
        output = xpath_parser(html_code, page_source)   
    elif sys.argv[1] == "C":
        from todo_3_implementation_name import name #change
        output = name(html_code, page_source)    #change
except Exception as error:
    print(error)

print(output)