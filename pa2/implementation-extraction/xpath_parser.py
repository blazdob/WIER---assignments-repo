#-*- coding: utf-8 -*-
from lxml import html
import json
import re

def remove_unwanted_characters(page_content):
	content = page_content.replace('\t', '').replace('\n', '').replace('\r', '')
	return ' '.join(content.split())

def xpath_parser(html_code, SOURCE_NAME):
	tree = html.fromstring(html_code)
	data = {}
	if "overstock" in SOURCE_NAME:
		objects = tree.xpath('//tbody/tr[(contains(@bgcolor, "#ffffff") or contains(@bgcolor, "#dddddd")) and count(td[@valign="top"]) = 2]/td[2]')
		for i in range(len(objects)):
			item = {
				"Title": "",
				"ListPrice": "",
				"Price": "",
				"Saving": "",
				"SavingPercent": "",
				"Content": ""
			}
			item['Title'] = objects[i].xpath('string(a/b/text())')
			item['ListPrice'] = objects[i].xpath('string(table/tbody/tr/td[1]/table/tbody/tr[1]/td[2]/s/text())')
			item['Price'] = objects[i].xpath('string(table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/span/b/text())')
			SavingAndPercent = objects[i].xpath('string(table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/span/text())').split(" ")
			item['Saving'] = SavingAndPercent[0]
			item['SavingPercent'] = SavingAndPercent[1][1:-1]
			item['Content'] = objects[i].xpath('string(table/tbody/tr/td[2]/span/text())')
			data[i] = item
		return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
	elif "rtvslo" in SOURCE_NAME:
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
		data[SOURCE_NAME] = item
		return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
	elif "bolha" in SOURCE_NAME:
		objects = tree.xpath('.//li[contains(@class, "EntityList-item EntityList-item--Regular EntityList-item--n")]')
		for i in range(len(objects)):
			item = {
				"Title": "",
				"Price": "",
				"PublishedTime": "",
				"Location": "",
			}
			item["Price"] = remove_unwanted_characters(objects[i].xpath('article//strong[@class="price price--hrk"]/text()')[0]) + "€"
			item["Title"] = remove_unwanted_characters(objects[i].xpath('article//h3[@class="entity-title"]/a/text()')[0])
			item["PublishedTime"] = remove_unwanted_characters(objects[i].xpath('article//time[@class="date date--full"]/text()')[0])
			item["Location"] = remove_unwanted_characters(objects[i].xpath('article//div[@class="entity-description-main"]/text()')[1])
			data[i] = item
		return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
	elif "siol" in SOURCE_NAME:
		item = {
			"Title": "",
			"Author": "",
			"PublishedTime": "",
			"Lead": "",
			"Content": ""
		}
		item["PublishedTime"] = remove_unwanted_characters("".join(tree.xpath('//span[@class= "article__publish_date"]/span[position()<4 and position()>1]/text()')))
		item["Title"] = remove_unwanted_characters(tree.xpath('//h1[@class= "article__title"]/text()')[0])
		item["Author"] = remove_unwanted_characters(tree.xpath('//span[@class= "article__author "]/a/text()')[0])
		item["Lead"] = remove_unwanted_characters(tree.xpath('//div[@class= "article__intro js_articleIntro"]/p/text()')[0])
		item["Content"] = remove_unwanted_characters("".join(tree.xpath('//div[@class= "article__main js_article js_bannerInArticleWrap"]/p[position()>0]/text()')))
		data[SOURCE_NAME] = item
		return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)