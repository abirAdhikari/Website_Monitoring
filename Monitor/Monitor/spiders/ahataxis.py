# Author: AADHIKARI 5/31/2018
import os 
import sys 
import scrapy
from datetime import datetime
from datetime import date
from datetime import timedelta
from time import sleep
from lxml import etree
import xml.etree.ElementTree as ET
from lxml import html 
from scrapy_splash import SplashRequest
import urllib
import urllib.request
from urllib.request import urlopen
from selenium import webdriver
import logging

sys.path.append('.')
sys.path.append('..')
from timedecorator import TimeDecorator
from scrapyutils import ScrapyUtils
from competitivedataitem import CompetitiveDataItem
from urlgenerator import UrlGenerator
from hawkeyeutils import *

class AhaTaxisSpider(scrapy.Spider):
	name = "ahataxis"
	
	def __init__(self, scheduler_id=None):
		self._scheduler_id = scheduler_id
		
			
	def start_requests(self):
		logging.log(logging.INFO, "AhaTaxisSpider::start_requests(*****): Enter [%s]" % self._scheduler_id)
		
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		urls = hawkeyetaskdata.get_current_urls_set(self.name)
		
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		browser = webdriver.Chrome(chrome_options=options) #replace with .Firefox(), or with the browser of your choice
		
		for url_meta in urls:
			hawkeyetaskdata.executing(self.name)
			this_url = url_meta['url']
			logging.log(logging.INFO, "AhaTaxisSpider::start_requests(*****): URL : %s" % this_url)
			# AADHIKARI - Splash is not able to render the javascript from ahataxis.com
			# So, browsing it with chrome and passing the inner text as metadata to the next parser 
			browser.get(this_url) #navigate to the page
			sleep(3)
			innerHTML = browser.execute_script("return document.body.innerHTML")
			#ScrapyUtils.write_to_io_file('ahataxis-before.html', innerHTML)
			'''
			meta={'splash':{'endpoint':'render.html','args':{'wait': 10,}}, 
				'url': this_url, 'trip_date': url_meta['trip_date'], 'src_city': url_meta['src_city'], 'dst_city': url_meta['dst_city'], 'innerHTML' : innerHTML}
			'''
			
			yield scrapy.Request(this_url, callback=self.parse, headers=ScrapyUtils.custom_header(),\
				meta={'splash':{'endpoint':'render.html','args':{'wait': 10,}}, 'url_meta': url_meta, 'innerHTML' : innerHTML})
			
		logging.log(logging.INFO, "AhaTaxisSpider::start_requests(*****): Exit[%s]" % self._scheduler_id)

	
	# WORKING PARSER
	def parse(self, response):
		
		logging.log(logging.INFO, 'AhaTaxisSpider::parse(*****): Enter')
		
		url_meta = response.meta['url_meta']
		innerHTML = response.meta['innerHTML']
		url =	response.url
		trip_date = url_meta['trip_date']
		src_city = url_meta['src_city']
		dst_city = url_meta['dst_city']
		
		error = False
		
		try:
			#ScrapyUtils.write_to_io_file('ahataxis-after.html', innerHTML)
			doc = html.fromstring(innerHTML)
		
			today_date = str(date.today())
			taxi_categories = doc.xpath('//*[@class="taxi_category res_design_diff ng-scope"]')
			
			logging.log(logging.INFO, 'AhaTaxisSpider::parse(*****): taxi_categories - %s' % (taxi_categories))
			for taxi_category in taxi_categories:
				cab_types = taxi_category.xpath('//*[@class="h3 ng-binding"]')
				cab_names = taxi_category.xpath('//*[@class="bold ng-binding"]')
				base_rates = taxi_category.xpath('//*[@class="priceInt ng-binding"]/span')
				prices = taxi_category.xpath('//*[@class="taxiRates ng-binding"]')
				
				logging.log(logging.INFO, 'AhaTaxisSpider::parse(*****): item - %s, %s, %s, %s' % (cab_types, cab_names, base_rates, prices))
			
				if len(base_rates) == 0:
					base_rates = prices
					
				for item in zip(cab_types,cab_names,base_rates, prices):
					cab_type = item[0].text
					cab_name = item[1].text
					passengers = ScrapyUtils.get_pax_count_from_cab_type(cab_type)
					markup_price = item[2].text[len(item[2].text)-1]
					price = ''.join(filter(lambda x: x.isdigit(), str(item[3].text)))
					
					logging.log(logging.INFO, "AhaTaxisSpider::parse(*****): Extracted Data: cab_type=%s, cab_name=%s, passangers=%s, markeup_price=%s, price=%s" %\
							(cab_type, cab_name, passengers, markup_price, price))
					
					normalized_cab_type = ScrapyUtils.normalize_cab_type(cab_type)	
					unique_id, md5_url = ScrapyUtils.get_unique_key(url_meta, cab_type)
					
					competitiveData = CompetitiveDataItem(
							unique_id=unique_id,
							md5_url=md5_url,
							collection_date=today_date,
							pickup_date=trip_date,
							trip_type='Oneway',
							vendor='AhaTaxis',
							src_city=src_city,
							dst_city=dst_city,
							cab_type=cab_type,
							normalized_cab_type=normalized_cab_type,
							cab_name=cab_name,
							pax_count=passengers,
							markup_price=int(price),
							base_price=int(price),
							poll_priority=self._scheduler_id,
							url=url)
									
								
					yield competitiveData
				
				# looping only once as top 'taxi_categories' just repeats itself
				break
				
			
		except Exception as e:
			logging.log(logging.ERROR, "AhaTaxisSpider::parse(*****): Error : %s" % e)
			error = True
			pass
		
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		if error == False:
			hawkeyetaskdata.success(self.name)
		else:
			hawkeyetaskdata.error(self.name)			
		
		logging.log(logging.INFO, 'AhaTaxisSpider::parse(*****): Exit')

	'''
	# NOT WORKING CURRENTLY
	def parse_css(self, in_response):
		
		url_meta = in_response.meta['url_meta']
		innerHTML = in_response.meta['innerHTML']
		trip_date = url_meta['trip_date']
		src_city = url_meta['src_city']
		dst_city = url_meta['dst_city']
		
		ScrapyUtils.write_to_io_file('ahataxis-innerHTML.html', str(innerHTML))
		ScrapyUtils.write_to_io_file('ahataxis-before-copy.html', str(in_response.body))
		
		in_response.replace(body=innerHTML.encode('utf-8'))
		response = in_response.copy()
		#ScrapyUtils.write_to_io_file('ahataxis-after-copy.html', str(in_response.body))
		
		try:
			#relevant_content = response.css('.row.div_content.select_page_row').extract()
			# class='h3 ng-binding'
			cab_types = response.css('.h3.ng-binding::text').extract()
			# class='bold ng-binding'
			cab_names = response.css('.bold.ng-binding::text').extract()
			# class='priceInt ng-binding'
			markup_prices = response.css('.priceInt.ng-binding::text').extract()
			# class='taxiRates ng-binding'
			prices = response.css('.taxiRates.ng-binding::text').extract()
			
			logging.log(logging.INFO, "AhaTaxisSpider::parse_css(*****): item=%s, %s, %s, %s" % 
				(cab_types, cab_names, markup_prices, prices))
			
			today_date = str(date.today())			
			for item in zip(cab_types,cab_names,markup_prices, prices):		
				cab_type = str[item[0]]
				cab_name = str(item[1])
				markup_price = str(''.join(filter(str.isdigit, item[2])))
				price = str(''.join(filter(str.isdigit, item[3])))
				passengers = ScrapyUtils.get_pax_count_from_cab_type(cab_type)	
				logging.log(logging.INFO, "AhaTaxisSpider::parse_css(*****): item = %s, %s, %s, %s, %s" % 
					(cab_type, cab_name, passengers, markup_price, price))
				
				normalized_cab_type = ScrapyUtils.normalize_cab_type(cab_type)
				unique_id, md5_url = ScrapyUtils.get_unique_key(url_meta, cab_type)
				competitiveData = CompetitiveDataItem(
						unique_id=unique_id,
						md5_url=md5_url,
						collection_date=today_date,
						pickup_date=trip_date,
						trip_type='Oneway',
						vendor='Wiwigo',
						src_city=src_city,
						dst_city=dst_city,
						cab_type=cab_type,
						normalized_cab_type=normalized_cab_type,
						cab_name=cab_name,
						pax_count=passengers,
						markup_price=price,
						base_price=price)
								
				return competitiveData
			
		except Exception as e:
			logging.log(logging.ERROR, e)
			pass
	'''