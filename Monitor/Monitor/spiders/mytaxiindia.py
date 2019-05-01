# AADHIKARI 6/31/2018
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

class MyTaxiIndiaSpider(scrapy.Spider):
	name = "mytaxiindia"
	
	def __init__(self, scheduler_id=None):
		self._scheduler_id = scheduler_id
		
		
	def start_requests(self):
		logging.log(logging.INFO, "MyTaxiIndiaSpider::start_requests(*****): Enter[%s]" % self._scheduler_id)
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		urls = hawkeyetaskdata.get_current_urls_set(self.name)
		
		for url_meta in urls:
			hawkeyetaskdata.executing(self.name)
			this_url = url_meta['url']
			formdata = url_meta['formdata']
			logging.log(logging.INFO, "MakeMyTripSpider::start_requests(*****): URL : %s, FormData = %s" % (this_url, formdata))
			yield scrapy.FormRequest(
				this_url,
				formdata=formdata,
				callback=self.parse_css,
				#meta={'url': this_url, 'trip_date': url_meta['trip_date'], 'src_city': url_meta['src_city'], 'dst_city': url_meta['dst_city'], 'formdata': formdata}
				meta={'url_meta': url_meta}
			)
			if hawkeyetaskdata.batch_finished(self.name) == True:
				break
		logging.log(logging.INFO, "MyTaxiIndiaSpider::start_requests(*****): Exit[%s]" % self._scheduler_id)
		
	def parse_css(self, response):
		logging.log(logging.INFO, "MyTaxiIndiaSpider::parse_css(*****): Enter")
		url_meta = response.meta['url_meta']
		trip_date = url_meta['trip_date']
		src_city = url_meta['src_city']
		dst_city = url_meta['dst_city']
		url = response.url
		
		error = False
		
		try:
			#logging.log(logging.INFO, "MyTaxiIndiaSpider::parse_css(*****): body = %s" % (response.body))
			# class='box-title text-center'
			cab_names = response.css('.box-title.text-center::text').extract()
			# class='amenities col-md-6'
			cab_passenger_counts = response.css('.amenities.col-md-6 li:nth-child(1)::text').extract()
			# class='faresummarybox'
			prices = response.css('.price-total::text').extract()
			
			# prices contains some special characters like Rs, lets filter them out
			# new_prices = []
			# parsed_count = len(cab_passenger_counts)
			# prices_count = len(prices)
			# multiplier = int(prices_count/parsed_count)
			# #logging.log(logging.INFO, "MyTaxiIndiaSpider::parse_css(*****): parsed_count = %s, prices_count = %s, multiplier = %s" % (parsed_count, prices_count, multiplier))
			# if prices_count > parsed_count:
				# for i in range(0, parsed_count):
					# price_index = (i * multiplier) + 1
					# #logging.log(logging.INFO, "MyTaxiIndiaSpider::parse_css(*****): i = %s, price_index = %s" % (i, price_index))
					# new_prices.insert(i, prices[price_index])
			
			#logging.log(logging.INFO, "MyTaxiIndiaSpider::parse_css(*****): item = %s, %s, %s" % (cab_names, cab_passenger_counts, new_prices))
				
			today_date = str(date.today())			
			for item in zip(cab_names,cab_passenger_counts,prices):		
				cab_name = ScrapyUtils.mytaxiindia_remove_junk_from_cab_name(str(item[0]))
				passengers = str(item[1])
				price = str(''.join(filter(str.isdigit, item[2])))
				cab_type = ScrapyUtils.mytaxiindia_get_cab_type_from_cab_name(cab_name)	
				logging.log(logging.INFO, "MyTaxiIndiaSpider::parse_css(*****): cab_type: %s, cab_name: %s, passengers: %s, price: %s" % (cab_type, cab_name, passengers, price))
				
				normalized_cab_type = ScrapyUtils.normalize_cab_type(cab_type)
				normalized_trip_date = ScrapyUtils.mytaxiindia_normalize_date(trip_date)
				unique_id, md5_url = ScrapyUtils.get_unique_key(url_meta, cab_type)
				
				competitiveData = CompetitiveDataItem(
						unique_id=unique_id,
						md5_url=md5_url,
						collection_date=today_date,
						pickup_date=normalized_trip_date,
						trip_type='Oneway',
						vendor='MyTaxiIndia',
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
			logging.log(logging.ERROR, "MyTaxiIndiaSpider::parse_css(*****): Error : %s" % e)	
			error = True
			pass
		
		hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
		if error == False:
			hawkeyetaskdata.success(self.name)
		else:
			hawkeyetaskdata.error(self.name)			
		
		logging.log(logging.INFO, "MyTaxiIndiaSpider::parse_css(*****): Exit")