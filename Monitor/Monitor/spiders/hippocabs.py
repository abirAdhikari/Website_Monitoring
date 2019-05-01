# AADHIKARI 6/31/2018
import os 
import sys 
import scrapy
from datetime import datetime
from datetime import date
from datetime import timedelta
from time import sleep
import xml.etree.ElementTree as ET
from lxml import html
import collections
import logging
from scrapy_splash import SplashRequest


sys.path.append('.')
sys.path.append('..')
from timedecorator import TimeDecorator
from scrapyutils import ScrapyUtils
from competitivedataitem import CompetitiveDataItem
from urlgenerator import UrlGenerator
from hawkeyeutils import *
from selenium import webdriver

'''
Form Data: view URL encoded
drp_start_city: Chandigarh
drp_end_city: Manali
txt_pickup: Chandigarh, India
txt_dropoff: Manali, Himachal Pradesh, India
txt_datetime: 04/03/19
drp_time: 09:00 AM
pas_contact1: 9876543210

drp_start_city: Chandigarh
drp_end_city: Manali
txt_pickup: Chandigarh%2C+India
txt_dropoff: Manali%2C+Himachal+Pradesh%2C+India
txt_datetime: 04%2F03%2F19
drp_time: 09%3A00+AM
pas_contact1: 9876543210


drp_start_city=Chandigarh&drp_end_city=Manali&txt_pickup=Chandigarh%2C+India&txt_dropoff=Manali%2C+Himachal+Pradesh%2C+India&txt_datetime=04%2F03%2F19&drp_time=09%3A00+AM&pas_contact1=9876543210


Request URL: https://hippocabs.com/web/search_cabs.php
Request Method: POST
Status Code: 200 OK
Remote Address: 13.126.106.232:443
Referrer Policy: no-referrer-when-downgrade
Access-Control-Allow-Origin: *
Cache-Control: no cache
Connection: Keep-Alive
Content-Encoding: gzip
Content-Length: 18723
Content-Type: text/html; charset=UTF-8
Date: Mon, 01 Apr 2019 16:51:00 GMT
Expires: Thu, 19 Nov 1981 08:52:00 GMT
Keep-Alive: timeout=5, max=500
Pragma: no-cache
Server: Apache
Set-Cookie: start_city=Chandigarh; expires=Wed, 01-May-2019 16:51:00 GMT; Max-Age=2592000; path=/
Set-Cookie: end_city=Manali; expires=Wed, 01-May-2019 16:51:00 GMT; Max-Age=2592000; path=/
Set-Cookie: pickup=Chandigarh%2C+India; expires=Wed, 01-May-2019 16:51:00 GMT; Max-Age=2592000; path=/
Set-Cookie: dropoff=Manali%2C+Himachal+Pradesh%2C+India; expires=Wed, 01-May-2019 16:51:00 GMT; Max-Age=2592000; path=/
Vary: Accept-Encoding
X-Powered-By: PHP/5.6.31
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Cache-Control: max-age=0
Connection: keep-alive
Content-Length: 194
Content-Type: application/x-www-form-urlencoded
Cookie: PHPSESSID=eom9p4jlovg0pp4l716fie0ts3; _gcl_au=1.1.1673962582.1554125794; _ga=GA1.2.306542050.1554125794; _gid=GA1.2.492969219.1554125794; _cio=199418ee-5d9c-3439-a5d7-1077661b1276; _hjIncludedInSample=1; SL_C_23361dd035530_KEY=bb37e148f36ad7537155d0e952d08dd8e6a2bbdf; start_city=Chandigarh; end_city=Manali; pickup=Chandigarh%2C+India; dropoff=Manali%2C+Himachal+Pradesh%2C+India; _gat_UA-74626310-1=1
Host: hippocabs.com
Origin: https://hippocabs.com
Referer: https://hippocabs.com/web/
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36
drp_start_city: Chandigarh
drp_end_city: Manali
txt_pickup: Chandigarh%2C+India
txt_dropoff: Manali%2C+Himachal+Pradesh%2C+India
txt_datetime: 04%2F03%2F19
drp_time: 09%3A00+AM
pas_contact1: 9876543210

'''

'''
formdata = {
        'drp_start_city':'Chandigarh', \
        'drp_end_city':'Manali',\
        'txt_pickup':'Chandigarh', \
        'txt_dropoff':'Manali',\
        'txt_datetime':'04/03/2019', 
        'drp_time':'09:00 AM',
        'pas_contact1':'9876543210'
    }
'''
class HippoCabsSpider(scrapy.Spider):
    name = "hippocabs"
    rotate_user_agent = True
    
    def __init__(self, scheduler_id=None):
        self._scheduler_id = scheduler_id
        
        
    def start_requests(self):
        print(logging.INFO, "HippoCabsSpider::start_requests(*****): Enter[%s]" % self._scheduler_id)
        hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
        urls = hawkeyetaskdata.get_current_urls_set(self.name)
        
        print ("URLS: ", urls)
        
        # options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # browser = webdriver.Chrome(chrome_options=options)
        
        for url_meta in urls:
            hawkeyetaskdata.executing(self.name)
            this_url = url_meta['url']
            formdata = url_meta['formdata']
            print ('URL: ', this_url, ', formdata: ', formdata, 'trip date: ',url_meta['trip_date'])         
                        
            yield scrapy.FormRequest(
                this_url,
                formdata=formdata,
                callback=self.parse_css,
                meta={'url': this_url, 'trip_date': url_meta['trip_date'], 'src_city': url_meta['src_city'], 'dst_city': url_meta['dst_city'], 'formdata': formdata}                
            )
            if hawkeyetaskdata.batch_finished(self.name) == True:
                break
                
        print(logging.INFO, "HippoCabsSpider::start_requests(*****): Exit[%s]" % self._scheduler_id)
        
    def parse_css(self, response):
        print(logging.INFO, "HippoCabsSpider::parse_css(*****): Enter")
        '''
        _file = open("test_op.html", 'a')
        _file.write(str(response.body))
        _file.close()
        '''
        
        url_meta = response.meta
        url = url_meta['url']
        #innerHTML = response.meta['innerHTML']
        #trip_date = TimeDecorator.normalize_date_for_database(url_meta['trip_date'])
        trip_date = url_meta['trip_date']
        src_city = url_meta['src_city']
        dst_city = url_meta['dst_city']
        url = response.url
        error = False
        
        print("***** From City: %s - To City: %s, Trip Date: %s*****" % (src_city, dst_city, trip_date))
        try:
            #print(logging.INFO, "HippoCabsSpider::parse_css(*****): body = %s" % (response.body))
            # class='box-title text-center'
            
            cab_names = response.css('.cars-info::text').extract()
            #print("Cabs:",cab_names)
            
            cab_details = response.css('.col-md-9.col-sm-12.cab-details')
            #print ("cab_details ", cab_details)
            prices = cab_details.css('.price::text').extract()
            #prices ['3932', '₹', '4961', '₹', '4362', '₹', '5491', '₹']
            # get only odd items which conatins price
            prices = prices[::2] 
            #print("prices",prices)         
            
            print(logging.INFO, "HippoCabsSpider::parse_css(*****): item = %s, %s" % (cab_names, prices))
            
            today_date = str(date.today())            
            
            if len(prices) != 0:
                
                for item in zip(cab_names,prices):        
                    cab_name = str(item[0])
                    price = str(''.join(filter(str.isdigit, item[1])))
                    cab_type = ScrapyUtils.hippocabs_get_cab_type_from_cab_name(cab_name)     
                    passengers = ScrapyUtils.get_pax_count_from_cab_type(cab_type)
                    print(logging.INFO, "HippoCabsSpider::parse_css(*****): cab_type: %s, cab_name: %s, passengers: %s, price: %s" % (cab_type, cab_name, passengers, price))
                    
                    normalized_cab_type = ScrapyUtils.normalize_cab_type(cab_type)
                    normalized_trip_date = ScrapyUtils.hippocabs_normalize_date(trip_date)
                    unique_id, md5_url = ScrapyUtils.get_unique_key(url_meta, cab_type)
                    
                    competitiveData = CompetitiveDataItem(
                            unique_id=unique_id,
                            md5_url=md5_url,
                            collection_date=today_date,
                            pickup_date=normalized_trip_date,
                            trip_type='Oneway',
                            vendor='HippoCabs',
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
            else:
                error = True
                
        except Exception as e:
            print(logging.ERROR, "HippoCabsSpider::parse_css(*****): Error : %s" % e)   
            error = True
            pass
        
        hawkeyetaskdata = HawkeyeTasks().Instance.get(self._scheduler_id)
        if error == False:
            hawkeyetaskdata.success(self.name)
        else:
            hawkeyetaskdata.error(self.name)          
        
        print(logging.INFO, "HippoCabsSpider::parse_css(*****): Exit")