# Author: AADHIKARI 5/31/2018
# https://doc.scrapy.org/en/0.10.3/topics/selectors.html
import os 
import sys 
import scrapy
from datetime import datetime
from datetime import date
from datetime import timedelta
import xml.etree.ElementTree as ET
import logging
from lxml import html 
from scrapy_splash import SplashRequest

sys.path.append('.')
sys.path.append('..')
from timedecorator import TimeDecorator
from scrapyutils import ScrapyUtils
from competitivedataitem import CompetitiveDataItem
from urlgenerator import UrlGenerator
from hawkeyeutils import *
from scrapy.http import Request

class MakeMyTripSpider(scrapy.Spider):
    name = "makemytrip"
    rotate_user_agent = True
    
    def __init__(self, scheduler_id=None):
        self._scheduler_id = scheduler_id
            
    def start_requests(self):
        logging.log(logging.INFO, "MakeMyTripSpider::start_requests_v1(*****): Enter[%s]" % self._scheduler_id)
        hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
        urls = hawkeyetaskdata.get_current_urls_set(self.name)
        
        #requests=[]
        for url_meta in urls:
            hawkeyetaskdata.executing(self.name)
            this_url = url_meta['url']
            logging.log(logging.INFO, "MakeMyTripSpider::start_requests_v1(*****): URL : %s" % this_url)
            #print("MakeMyTripSpider::start_requests_v1(*****): URL : %s" % this_url)
            '''
            meta={'splash':{'endpoint':'render.html','args':{'wait': 10,}}, 
            'url': url_meta['url'], 'trip_date': url_meta['trip_date'],
            'src_city': url_meta['src_city'], 'dst_city': url_meta['dst_city']}
            '''
            
            # requests.append(Request(url="https://cabs.makemytrip.com/desktop/search",headers={'Referer':this_url}))
                                         # #   'content_type':'application/json','Accept':'application/json'}))
                                            
                                            
                                            
            #print(requests)
            
            yield scrapy.Request(this_url, callback=self.parse, headers=ScrapyUtils.custom_header(),\
                meta={'splash':{'endpoint':'render.html','args':{'wait': 10,}}, 'url_meta': url_meta})
            if hawkeyetaskdata.batch_finished(self.name) == True:
                break
                
            # yield scrapy.Request("https://cabs.makemytrip.com/desktop/search", callback=self.parse, headers={'Referer':this_url},\
                # meta={'splash':{'endpoint':'render.html','args':{'wait': 10,}}, 'url_meta': url_meta})
            # if hawkeyetaskdata.batch_finished(self.name) == True:
                # break
        logging.log(logging.INFO, "MakeMyTripSpider::start_requests_v1(*****): Exit[%s]" % self._scheduler_id)
            
        
    def parse(self, response):
    
    
        _file = open("test_op.html", 'a')
        _file.write(str(response.body))
        _file.close()
        
    
        url_meta = response.meta['url_meta']
        
        trip_date = TimeDecorator.normalize_date_for_database(url_meta['trip_date'])
        src_city = url_meta['src_city']
        dst_city = url_meta['dst_city']
        url = response.url
        
        error = False
        #ScrapyUtils.write_to_io_file('makemytrip-after.html', str(response.body))
        try:
            # class='car lato-bold'
            cab_types = response.css('.car.lato-bold::text').extract()
            
             
            # print("Cabs",cab_types)
            # class='car_type_des append_bottom6'
            cab_names = response.css('.car_type_des.append_bottom6::text').extract()            
            # class='type_one grey lato-regular append_bottom6'
            #cab_passenger_counts = response.css('.type_one.grey.lato-regular.append_bottom6::text').extract()
            # mt-id='car_price'
            #car_prices = response.css('.actual_price.lato-medium').extract()
            car_prices = response.xpath('//span[@mt-id="car_price"]/text()').extract()
            # mt-id='markup_amount'
            #markup_prices = response.css('.slashed_price.grey.lato-medium').extract()
            markup_prices = response.xpath('//span[@mt-id="markup_amount"]/text()').extract()
            
            
            
            
            logging.log(logging.INFO, "MakeMyTripSpider::parse_css(*****): %s, %s, %s, %s" % 
                    (cab_types, cab_names, car_prices, markup_prices))
            
            today_date = str(date.today())          
            for item in zip(cab_types,cab_names, car_prices, markup_prices):        
                cab_type = str(item[0])
                cab_name = str(item[1])
                passengers = ScrapyUtils.get_pax_count_from_cab_type(cab_type)
                
                price = str(''.join(filter(str.isdigit, item[2])))
                markup_price = str(''.join(filter(str.isdigit, item[3])))
                
                logging.log(logging.INFO, "MakeMyTripSpider::parse_css(*****): item = %s, %s, %s, %s, %s" % 
                        (cab_type, cab_name, passengers, price, markup_price))
                
                
                #print('Markup_price:',markup_price)
                
                normalized_cab_type = ScrapyUtils.normalize_cab_type(cab_type)  
                unique_id, md5_url = ScrapyUtils.get_unique_key(url_meta, cab_type)
                competitiveData = CompetitiveDataItem(
                        unique_id=unique_id,
                        md5_url=md5_url,
                        collection_date=today_date,
                        pickup_date=trip_date,
                        trip_type='Oneway',
                        vendor='MakeMyTrip',
                        src_city=src_city,
                        dst_city=dst_city,
                        cab_type=cab_type,
                        normalized_cab_type=normalized_cab_type,
                        cab_name=cab_name,
                        pax_count=passengers,
                        markup_price=markup_price,
                        base_price=price,
                        poll_priority=self._scheduler_id,
                        url=url)
                
                yield competitiveData
            
        except Exception as e:
            logging.log(logging.ERROR, "MakeMyTripSpider::parse_css(*****): Error : %s" % e)
            error = True
            pass
        
        hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
        if error == False:
            hawkeyetaskdata.success(self.name)
        else:
            hawkeyetaskdata.error(self.name)            
        
        logging.log(logging.INFO, 'MakeMyTripSpider::parse_css(*****): Exit')