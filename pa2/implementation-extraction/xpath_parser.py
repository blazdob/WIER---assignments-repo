from lxml import html
import json
import re

def xpath_parser(html_code, SOURCE_NAME):
	tree = html.fromstring(html_code)
	data = {}
	if SOURCE_NAME == "overstock":
		

		objects = tree.xpath('//tbody/tr[(contains(@bgcolor, "#ffffff") or contains(@bgcolor, "#dddddd")) and count(td[@valign="top"]) = 2]/td[2]')

		for i in range(len(objects)):
		    item = {}
		    Title = objects[i].xpath('string(a/b/text())')
		    ListPrice = objects[i].xpath('string(table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text())')
		    Price = objects[i].xpath('string(table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text())')
		    SavingAndPercent = (objects[i].xpath('string(table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text())')).split(" ")
		    Saving = SavingAndPercent[0]
		    SavingPercent = SavingAndPercent[1]
		    Content = objects[i].xpath('string(table/tbody/tr/td[2]/span/text())')

		    item['Title'] = Title
		    item['ListPrice'] = ListPrice
		    item['Price'] = Price
		    item['Saving'] = Saving
		    item['SavingPercent'] = SavingPercent
		    item['Content'] = Content
		    data[i] = item
		#print(data)
		return 0#json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
	elif SOURCE_NAME == "rtvslo":
		item = {
            "Title": "",
            "SubTitle": "",
            "Author": "",
            "PublishedTime": "",
            "Lead": "",
            "Content": ""
        }
		item['Author'] = tree.xpath('//div[@class="author-name"]/text()')[0]
		item['PublishedTime'] = (tree.xpath('//*[@id="main-container"]/div[3]/div/div[1]/div[2]/text()'))[0].lstrip().rstrip()#[3:29]
		item['Title'] = tree.xpath('//header[@class="article-header"]/h1/text()')[0]
		item['SubTitle'] = tree.xpath('//header[@class="article-header"]/div[@class="subtitle"]/text()')[0]
		item['Lead'] = tree.xpath('//header[@class="article-header"]/p[@class="lead"]/text()')[0]
		# TODO CO2
		item["Content"] = '\n'.join(tree.xpath('//article[@class="article"]/p//text()'))

		print(item)
		print(item['Content'])

	elif SOURCE_NAME == "TRETJA":
		return 0