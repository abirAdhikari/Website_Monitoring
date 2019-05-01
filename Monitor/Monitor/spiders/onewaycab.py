# Author: AADHIKARI 5/31/2018
import os 
import sys 
import scrapy
from datetime import datetime
from datetime import date
from datetime import timedelta
import xml.etree.ElementTree as ET
from lxml import html
import collections
import logging

sys.path.append('.')
sys.path.append('..')
from timedecorator import TimeDecorator
from scrapyutils import ScrapyUtils
from competitivedataitem import CompetitiveDataItem
from urlgenerator import UrlGenerator
from hawkeyeutils import *


class OnewayCabSpider(scrapy.Spider):
	name = "onewaycab"
	rotate_user_agent = True
	
	def __init__(self, scheduler_id=None):
		self._scheduler_id = scheduler_id
	
			
	def start_requests(self):
		logging.log(logging.INFO, "OnewayCabSpider::start_requests(*****): Enter[%s]" % self._scheduler_id)
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		urls = hawkeyetaskdata.get_current_urls_set(self.name)
		
		for url_meta in urls:
			hawkeyetaskdata.executing(self.name)
			this_url = url_meta['url']
			logging.log(logging.INFO, "OnewayCabSpider::start_requests(*****): URL : %s" % this_url)
			yield scrapy.Request(url=this_url, callback=self.parse_css, meta={'url_meta': url_meta})			
			
		logging.log(logging.INFO, "OnewayCabSpider::start_requests(*****): Exit[%s]" % self._scheduler_id)
	
		
	
	def parse_css(self, response):
		url_meta = response.meta['url_meta']
		src_city = url_meta['src_city']
		dst_city = url_meta['dst_city']
		trip_date = url_meta['trip_date']
		url = response.url
		
		error = False
		
		try:
			today_date = str(date.today())
			# class='col-xs-6 mm_box_left'
			type_label = response.css('.col-xs-6.mm_box_left::text').extract()
			# col-xs-6 mm_box_right
			type_value = response.css('.col-xs-6.mm_box_right::text').extract()
			
			logging.log(logging.INFO, "OnewayCabSpider::parse_css(*****): %s, %s" % (type_label, type_value))
			# we get flat list like below [[A, a]...[E, e], [A, a]...[E, e]], so making container_size = 5
			container_size = 5
			loop_count = 0
			
			cab_type 	= ''
			rate 		= ''
			
			for item in zip(type_label,type_value):
				loop_count += 1
				
				if 'Cab Type' in item[0]:
					cab_type = item[1].strip(' ').strip(':').strip(' ')
				elif 'Cab Rate' in item[0]:
					rate = item[1]
				
				if loop_count == container_size:
					# one item iterated
					loop_count = 0
					passengers = ScrapyUtils.get_pax_count_from_cab_type(cab_type)
					cab_name = ScrapyUtils.get_cab_name_from_cab_type(cab_type)
					price = str(''.join(filter(str.isdigit, rate)))
					logging.log(logging.INFO, "OnewayCabSpider::parse_css(*****): item = %s, %s, %s, %s" % 
						(cab_type, cab_name, passengers, price))
					timeDecorator = TimeDecorator()
					normalized_cab_type = ScrapyUtils.normalize_cab_type(cab_type)	
					
					unique_id, md5_url = ScrapyUtils.get_unique_key(url_meta, cab_type)
					competitiveData = CompetitiveDataItem(
							unique_id=unique_id,
							md5_url=md5_url,
							collection_date=today_date,
							pickup_date=trip_date,
							trip_type='Oneway',
							vendor='OnewayCab',
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
			logging.log(logging.ERROR, "OnewayCabSpider::parse_css(*****): Error : %s" % e)
			error = True
			pass
		
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		if error == False:
			hawkeyetaskdata.success(self.name)
		else:
			hawkeyetaskdata.error(self.name)	
			
		logging.log(logging.INFO, 'OnewayCabSpider::parse_css(*****): Exit')
	
	'''
		
	def parse(self, response):
		url_meta = response.meta['url_meta']
		src_city = url_meta['src_city']
		dst_city = url_meta['dst_city']
		
		try:
			doc = html.fromstring(response.body)
			today_date = str(date.today())
			
			available_vehicle_rows_xpath = doc.xpath('//*[@class="col-md-4 col-xs-12"]')
			for available_vehicle_xpath in available_vehicle_rows_xpath:
				cab_type = ""
				name = ""
				passengers = ""
				price = ""
				
				key_value_pair=collections.defaultdict(str)
				key = ""
				value = ""
				for element in available_vehicle_xpath.iter():
					class_name = element.get("class")
					#logging.log(logging.INFOOnewayCabSpider::parse_css(*****): "%s - %s - %s" % (class_name, element.tag, element.text))
					if class_name == "col-xs-6 mm_box_left":
						if element.text == "Cab Type" or element.text == "Cab Rate":
							key = element.text
					if len(key) != 0 and class_name == "col-xs-6 mm_box_right":
						value = element.text
						if key == "Cab Type":
							cab_type = element.text.lstrip()							
						elif key == "Cab Rate":
							price = element.text
							price = ''.join(filter(lambda x: x.isdigit(), price))
						
					if element.text != None and element.text.find("Available Cabs") != -1:
						key = "Available Cabs"
						value = element.text[17:]
						name = element.text[17:]
					
					if len(key) != 0 and len(value) != 0:
						key = ""
						value = ""
						if 	len(name) != 0 and len(price) != 0: 
							# OnewayCab has flat rate for all dates
							timeDecorator = TimeDecorator()
							for trip_date in timeDecorator.get_oneway_date_range('onewaycab'):
								if passengers == '':
									if 'Swift' in name:
										passengers = "4 Passenger Seats"
									elif 'Innova' in name:
										passengers = "6 Passenger Seats"
								ScrapyUtils.write_to_file('AhaTaxis_', 
									trip_date, today_date, 
									'OnewayCab', 
									src_city, dst_city, 
									cab_type, name, 
									passengers, price)
			
		except Exception as e:
			logging.log(logging.ERROR, e)
			pass
		
	'''