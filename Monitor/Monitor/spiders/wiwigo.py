# Author: AADHIKARI 5/31/2018
import os 
import sys 
import scrapy
from datetime import datetime
from datetime import date
from datetime import timedelta
import xml.etree.ElementTree as ET
from lxml import html 
import logging

sys.path.append('.')
sys.path.append('..')
from timedecorator import TimeDecorator
from scrapyutils import ScrapyUtils
from competitivedataitem import CompetitiveDataItem
from urlgenerator import UrlGenerator
from hawkeyeutils import *


class WiwigoSpider(scrapy.Spider):
	name = "wiwigo"
	rotate_user_agent = True
	
	def __init__(self, scheduler_id=None):
		self._scheduler_id = scheduler_id
		
	def start_requests(self):
		logging.log(logging.INFO, "WiwigoSpider::start_requests(*****): Enter [%s]" % self._scheduler_id)
		
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		urls = hawkeyetaskdata.get_current_urls_set(self.name)
		
		for url_meta in urls:
			hawkeyetaskdata.executing(self.name)
			this_url = url_meta['url']
			logging.log(logging.INFO, "WiwigoSpider::start_requests(*****): URL : %s" % this_url)
			yield scrapy.Request(url=this_url, callback=self.parse_css, 
				meta={'url_meta': url_meta})	
			
		logging.log(logging.INFO, "WiwigoSpider::start_requests(*****): Exit[%s]" % self._scheduler_id)
	
	
	def parse_css(self, response):
		
		url_meta = response.meta['url_meta']
		trip_date = url_meta['trip_date']
		src_city = url_meta['src_city']
		dst_city = url_meta['dst_city']
		url = response.url
		
		error = False
		
		try:
			# class='car-name'
			cab_names = response.css('.car-name::text').extract()
			# class='passengers row col-xs-12'
			cab_passenger_counts = response.css('.passengers.row.col-xs-12::text').extract()
			# class='cost'
			prices = response.css('.cost::text').extract()
			today_date = str(date.today())			
			for item in zip(cab_names,cab_passenger_counts,prices):		
				cab_name = str(item[0])
				passengers = str(item[1])
				price = str(''.join(filter(str.isdigit, item[2])))
				# wiwwigo doesn't publish cab_type explicidly
				cab_type = ScrapyUtils.wiwigo_get_cab_type_from_cab_name(cab_name)	
				normalized_cab_type = ScrapyUtils.normalize_cab_type(cab_type)
			
				logging.log(logging.INFO, "WiwigoSpider::parse_css(*****): item = %s, %s, %s, %s" % (cab_type, cab_name, passengers, price))
				
				
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
						base_price=price,
						poll_priority=self._scheduler_id,
						url=url)
			
				yield competitiveData
			
			
		except Exception as e:
			logging.log(logging.ERROR, "WiwigoSpider::parse_css(*****): Error : %s" % e)	
			error = True
			pass
		
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		if error == False:
			hawkeyetaskdata.success(self.name)
		else:
			hawkeyetaskdata.error(self.name)			
			
		logging.log(logging.INFO, 'WiwigoSpider::parse_css(*****): Exit')
	'''
	def parse(self, response):
		url_meta = response.meta['url_meta']
		trip_date = url_meta['trip_date']
		src_city = url_meta['src_city']
		dst_city = url_meta['dst_city']
		
		try:
			doc = html.fromstring(response.body)
			today_date = str(date.today())
			available_vehicle_rows_xpath = doc.xpath('//*[@class="col-sm-8"]')
			
			for available_vehicle_xpath in available_vehicle_rows_xpath:
				cab_type = ""
				name = ""
				passengers = ""
				price = ""
				for element in available_vehicle_xpath.iter():
					class_name = element.get("class")
					logging.log(logging.INFO, "WiwigoSpider::parse(*****): item = %s - %s - %s" % (class_name, element.tag, element.text))
					if class_name == "car-name":
						name = element.text
						if name.find("Indica") != -1 or name.find("Ritz") != -1:
							cab_type = "AC HATCHBACK"
						elif name.find("Swift Dzire") != -1 or name.find(" Toyota Etios") != -1:
							cab_type = "AC SEDAN"
						elif name.find("Toyota Innova") != -1 or name.find("Xylo ") != -1:
							cab_type = "AC SUV"
						elif name.find("Tempo Traveller") != -1:
							cab_type = "AC TEMPO TRAVELLER"						
						else:
							cab_type = "Unknown"
					elif class_name == "passengers row col-xs-12":
						passengers = element.text
					elif class_name == "cost":
						price = element.text
						price = ''.join(filter(lambda x: x.isdigit(), price))
				
		except Exception as e:
			logging.log(logging.INFO, "WiwigoSpider::parse(*****): Error : %s" % e, level=log.ERROR)	
			pass
		
	'''