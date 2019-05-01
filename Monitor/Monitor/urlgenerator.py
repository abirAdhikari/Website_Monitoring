# Author: AADHIKARI 06/06/2018
'''
How to parse JSON files?
https://stackoverflow.com/questions/21058935/python-json-loads-shows-valueerror-extra-data
'''
import os 
import sys 
import logging
import random
import pandas as pd
import json
from pandas.io.json import json_normalize
import urllib
from lxml import etree
import xml.etree.ElementTree as ET
from timedecorator import TimeDecorator

from sqlite3 import dbapi2 as sqlite
import hashlib

def print_x(msg):
    print(msg)
    pass
    
class UrlGenerator(object):

    '''Singelton Start''' 
    class __UrlGenerator:
        def __init__(self):
            self.init_vendor_routes()
            self.init_polling_routes()
            
        def init_vendor_routes(self):
            self._gozo_df       = self.init_gozo_routes()
            self._makemytrip_df = self.init_makemytrip_routes()
            self._ahataxis_df   = self.init_ahataxis_routes()
            self._wiwigo_df     = self.init_wiwigo_routes()
            self._oneway_df     = self.init_onewaycab_routes()
            self._mytaxiindia_df = self.init_mytaxiindia_routes()
            self._getmecab_df    = self.init_getmecab_routes()
            self._hippocabs_df   = self.init_hippocabs_routes()
            
        def init_gozo_routes(self):
            gozo_input_json = os.getcwd() + '.\\spiders\\resources\\served_cities_gozo.json'    
            with open(gozo_input_json) as gozo_data_file: 
                gozo_content = gozo_data_file.read()
            gozo_content = '[' + gozo_content + ']'
            gozo_content = json.loads(gozo_content)
            gozo_df = pd.DataFrame(json_normalize(gozo_content))
            gozo_df = gozo_df.drop_duplicates()
            gozo_df['city_name'] = gozo_df.text.str.split(',', 1)
            gozo_df[['city_name','state']] = pd.DataFrame(gozo_df.city_name.values.tolist(), index= gozo_df.index)
            gozo_df['state'] = gozo_df.state.str.strip(' ')
            return gozo_df.reset_index()
        
        def find_city_name(x):
            gozoLoc = self.Instance._gozo_df.loc[x]
            print(x.gozoLoc.city_name)
            return gozoLoc.city_name

        def init_makemytrip_routes(self):
            mmt_input_json = os.getcwd() + '.\\spiders\\resources\\served_cities_makemytrip.json'
            with open(mmt_input_json) as data_file: 
                content = data_file.read()
            content = '[' + content + ']'
            content = json.loads(content)           
            mmt_df = pd.DataFrame(json_normalize(content))
            return mmt_df.reset_index()

        def init_mytaxiindia_routes(self):
            mytaxiindia_input_json = os.getcwd() + '.\\spiders\\resources\\served_cities_mytaxiindia.json'
            with open(mytaxiindia_input_json) as data_file: 
                content = data_file.read()
            content = '[' + content + ']'
            content = json.loads(content)           
            mytaxiindia_df = pd.DataFrame(json_normalize(content))
            return mytaxiindia_df.reset_index()

            
        def init_ahataxis_routes(self):
            pass
            
        def init_wiwigo_routes(self):
            pass
            
        def init_onewaycab_routes(self):
            pass
        
        def init_getmecab_routes(self):
            pass
        
        
        def init_hippocabs_routes(self):
            mytaxiindia_input_json = os.getcwd() + '.\\spiders\\resources\\served_cities_mytaxiindia.json'
            with open(mytaxiindia_input_json) as data_file: 
                content = data_file.read()
            content = '[' + content + ']'
            content = json.loads(content)           
            hippocabs_df = pd.DataFrame(json_normalize(content))
            return hippocabs_df.reset_index()
        
        def init_polling_routes(self):
            #resource_file = os.getcwd() + '.\\spiders\\resources\\routes_data.csv'
            resource_file = os.getcwd() + '.\\spiders\\resources\\routes_data_stripped.csv'
            
            df = pd.read_csv(resource_file, low_memory=False)
            df = df.filter(['INDEX', 'SOURCE','DESTINATION','POLL_PRIORITY'], axis=1)
            self._high_priority_df = df.loc[df['POLL_PRIORITY'] == 'HIGH_PRIORITY']
            self._moderate_priority_df = df.loc[df['POLL_PRIORITY'] == 'MODERATE_PRIORITY']
            self._low_priority_df = df.loc[df['POLL_PRIORITY'] == 'LOW_PRIORITY']
            
    Instance = None

    '''Singelton End''' 

    # MakeMyTrip
    _makemytrip_domain_url = 'https://cabs.makemytrip.com/dt_cabsListing?' 
    _makemytrip_query_url = 'fromCity=%s&toCity=%s&tripType=OW&'
    _makemytrip_date_url = 'departDate=%s&returnDate=%s&pickupTime=%s'
    _makemytrip_src_dest_url_docorator = '{"address":"%s","latitude":%s,"longitude":%s,"pincode":"","place_id":"%s","is_city":true}'

    # AhaTaxis
    _ahataxis_domain_url = 'https://www.ahataxis.com/select/?'
    _ahataxis_query_url = 'trip=%s&fromCity=%s&toCity=%s'
    _ahataxis_date_url = '&startDate=%s&pickupTime=%s'
    
    # OnewayCab
    _onewaycab_domain_url = 'https://oneway.cab/outstation/'
    _onewaycab_query_url = '%s-to-%s-taxi'

    # Wiwigo
    _wiwigo_domain_url = 'https://www.wiwigo.com/onesearch?'
    _wiwigo_query_url = 'from=%s&to=%s'
    _wiwigo_date_url = '&start=%s'
    
    
    # GozoCabs
    _gozo_domain_url = 'https://www.gozocabs.com/api/agent/booking/getCurrentQuote?'    
    _gozo_api_key    = 'api=DC4E575B3EFFEF7C64F2C40A6E829627&'
    _gozo_query_url  = 'pickupCity=%s&dropCity=%s&tripType=1&'
    _gozo_date_url   = 'pickupDate=%s&pickupTime=%s'
    
    
    
    #getmecab
    _getmecab_domain_url = 'https://www.getmecab.com/one-way/'
    _getmecab_query_url = '%s/%s'
    #_getmecab_date_url = '&start=%s'
    

    # MyTaxiIndia
    _mytaxiindia_domain_url = 'http://www.mytaxiindia.com/outstationcar'
    
    
    #HippoCabs
    #_hippocabs_domain_url= 'https://hippocabs.com/web/'
    _hippocabs_domain_url  = 'https://hippocabs.com/web/search_cabs.php'    
    
    def __init__(self, scheduler_id, vendor, dtimeDecorator, forced_refresh):
        
        if not UrlGenerator.Instance:
            UrlGenerator.Instance = UrlGenerator.__UrlGenerator()

        self._scheduler_id = scheduler_id
        self._vendor = vendor
        self._timeDecorator = dtimeDecorator
        self._forced_refresh = forced_refresh
        
        self._src_cities = []
        self._dst_cities = []

        self.populate_cities()
        self.hippo_content = None
        
        
    def normalize_makemytrip_city_names(self, cities):
        return cities

    def normalize_ahataxis_city_names(self, cities):
        return cities

    def normalize_onewaycab_city_names(self, cities):
        return cities

    def normalize_wiwigo_city_names(self, cities):
        return cities

    def normalize_mytaxiindia_city_names(self, cities):
        return cities
        
    def normalize_gozo_city_names(self, cities):
        return cities
        
    
    def normalize_getmecab_city_names(self, cities):
        return cities
        
        
    def normalize_hippocabs_city_names(self,cities):
        return cities
        
        
    # def get_hippo_pickup_dropoff(self,elem):
        # if self.hippo_content == None:                
            # hippocabs_input_json= os.getcwd()+ '.\\spiders\\resources\\india_states_cities.json'
            # with open(hippocabs_input_json,'r') as _file:
                # self.hippo_content = json.loads(_file.read())
        # print (self.hippo_content)
        # for state in self.hippo_content.keys():
            # if elem in self.hippo_content[state]:
                # content = '{},{},{}'.format(elem,state,'India')
                # print(content)
                # return '{},{},{}'.format(elem,state,'India')
                # #return elem+','+state+',India'
        
        
    def gen_phone(self):
        first = '998' #str(random.randint(100,999))
        second = str(random.randint(1,888)).zfill(3)

        last = (str(random.randint(1,9998)).zfill(4))
        while last in ['1111','2222','3333','4444','5555','6666','7777','8888']:
            last = (str(random.randint(1,9998)).zfill(4))

        return '{}{}{}'.format(first,second, last)

    def populate_cities(self):

        df = self.Instance._high_priority_df
        if self._scheduler_id == 'HIGH_PRIORITY':
            df = self.Instance._high_priority_df
        elif self._scheduler_id == 'MODERATE_PRIORITY':
            df = self.Instance._moderate_priority_df
        elif self._scheduler_id == 'LOW_PRIORITY':
            df = self.Instance._low_priority_df
         
        self._src_cities = df['SOURCE'].tolist()
        self._dst_cities = df['DESTINATION'].tolist()
    
        for pair in zip(self._src_cities, self._dst_cities):
            logging.log(logging.INFO, "UrlGenerator::populate_cities(#####) %s: From City: %s, To City: %s" % (self._scheduler_id, pair[0], pair[1]))
    
    def get_filtered_urls(self, selected_days):
        urls = self.get_urls(selected_days)
        if self._forced_refresh == True:
            return urls
        else:
            filtered_urls = []
            connection = sqlite.connect('spiders\sqlDb\competitiondatabase.db')
            cursor = connection.cursor()
            for url_meta in urls:
                m=hashlib.md5(bytes(str(url_meta),"ascii"))   # python 3
                url_md5 = m.hexdigest()
                print ("url_meta = %s, url_md5 = %s" % (url_meta, url_md5))
                cursor.execute("select * from competitiondata where url_md5=?", url_md5[0])
                result = cursor.fetchone()
                if result == False:
                    filtered_urls.append(url_meta)
            connection.close()
            return filtered_urls
        
        
    def get_urls(self, selected_days):
        if self._vendor == 'makemytrip':
            return self.get_makemytrip_urls(selected_days)
        if self._vendor == 'ahataxis':
            return self.get_ahataxis_urls(selected_days)
        if self._vendor == 'onewaycab':
            return self.get_onewaycab_urls(selected_days)
        if self._vendor == 'gozo':
            return self.get_gozo_urls(selected_days)
        if self._vendor == 'wiwigo':
            return self.get_wiwigo_urls(selected_days)
        if self._vendor == 'mytaxiindia':
            return self.get_mytaxiindia_urls(selected_days)
        if self._vendor == 'getmecab':
            return self.get_getmecab_urls(selected_days)
        if self._vendor== 'hippocabs':
            return self.get_hippocabs_urls(selected_days)
        print_x ("NO VENDOR FOUND")
        
    def get_makemytrip_urls(self, selected_days):

        normalized_src_cities = self.normalize_makemytrip_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_makemytrip_city_names(self._dst_cities)
        
        df = self.Instance._makemytrip_df.copy()
        urls = []

        for trip_date in self._timeDecorator.get_oneway_date_range('makemytrip', selected_days):
            for pair in zip(normalized_src_cities, normalized_dst_cities):
                src_city = pair[0]
                dst_city = pair[1]
                
                if src_city == dst_city:
                    continue            
                src_df = df[df['city_name'] == src_city]
                if (src_df.empty):
                    continue
                dest_df = df[df['city_name'] == dst_city]
                if (dest_df.empty):
                    continue
                
                print_x("*****[Scheduler=%s, Vendor=%s] From City: %s - To City: %s *****" % (self._scheduler_id, self._vendor, src_city, dst_city))
                src_url = ''
                for src_row in src_df.itertuples():    
                    src_url = (self._makemytrip_src_dest_url_docorator % (src_row.city_name, src_row.latitude, src_row.longitude, src_row.place_id))
                dest_url = ''
                for dest_row in dest_df.itertuples():            
                    dest_url = (self._makemytrip_src_dest_url_docorator % (dest_row.city_name, dest_row.latitude, dest_row.longitude, dest_row.place_id))
                
                query_url = (self._makemytrip_query_url % (src_url, dest_url))
                
                date_url = (self._makemytrip_date_url % (trip_date, '', '09:00'))
                this_url = self._makemytrip_domain_url + query_url + date_url
                print_x(this_url)
                metadata = {'src_city': src_city, 'dst_city': dst_city, 'trip_date': trip_date, 'url': this_url}
                urls.append(metadata)
            
        return urls

    def get_makemytrip_popular_destination_urls(self, selected_days):
        normalized_src_cities = self.normalize_makemytrip_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_makemytrip_city_names(self._dst_cities)

        pop_dest_df = self.Instance._makemytrip_df.copy()
        urls = []
        for trip_date in self._timeDecorator.get_oneway_date_range('makemytrip', selected_days):
            for src_row in pop_dest_df.itertuples():
                src_url = (self._makemytrip_src_dest_url_docorator % (src_row.city_name, src_row.latitude, src_row.longitude, src_row.place_id))
                for pop_dest in src_row.pop_dest:
                    dest_df = pop_dest_df[pop_dest_df['city_code'] == pop_dest]
                    for dest_row in dest_df.itertuples():
                        dest_url = (self._makemytrip_src_dest_url_docorator % (dest_row.city_name, dest_row.latitude, dest_row.longitude, dest_row.place_id))
                        query_url = (self._makemytrip_query_url % (src_url, dest_url))
                        print_x("***** From City: %s - To City: %s *****" % (src_row.city_name, dest_row.city_name))
                        date_url = (self._makemytrip_date_url % (trip_date, '', '09:00'))
                        this_url = self._makemytrip_domain_url + query_url + date_url
                        metadata = {'src_city': src_row.city_name, 'dst_city': dest_row.city_name, 'trip_date': trip_date, 'url': this_url }
                        urls.append(metadata) 
        return urls
        
        
        
    def get_gozo_urls(self, selected_days):
        normalized_src_cities = self.normalize_gozo_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_gozo_city_names(self._dst_cities)
        df = self.Instance._gozo_df.copy()
        urls = []
        for pair in zip(normalized_src_cities, normalized_dst_cities):
            src_city = pair[0]
            dst_city = pair[1]
            if src_city == dst_city:
                continue       
            src_df = df[df['city_name'] == src_city]
            if (src_df.empty):
                continue
            dest_df = df[df['city_name'] == dst_city]
            if (dest_df.empty):
                continue
            src_city_name = ''
            src_city_id = ''
            for src_row in src_df.itertuples():   
                src_city_name = src_row.city_name
                src_city_id = src_row.Index
            dest_city_name = ''
            dest_city_id = ''
            for dest_row in dest_df.itertuples():   
                dest_city_name = dest_row.city_name
                dest_city_id = dest_row.Index
            print("***** From City: %s (%s) - To City: %s (%s)*****" % (src_city, src_city_id, dst_city, dest_city_id))
            query_url = (self._gozo_query_url % (src_city_id, dest_city_id))
            for trip_date in self._timeDecorator.get_oneway_date_range('gozo', selected_days):
                date_url = (self._gozo_date_url % (str(trip_date), '09:00'))
                this_url = self._gozo_domain_url + self._gozo_api_key + query_url + date_url
                metadata = {'src_city': src_city, 'dst_city': dst_city, 'trip_date': trip_date, 'url': this_url}
                urls.append(metadata)
                
        return urls


    
    def get_ahataxis_urls(self, selected_days):
        normalized_src_cities = self.normalize_ahataxis_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_ahataxis_city_names(self._dst_cities)

        urls = []
        for trip_date in self._timeDecorator.get_oneway_date_range('ahataxis', selected_days):
            for pair in zip(normalized_src_cities, normalized_dst_cities):
                src_city = pair[0]
                dst_city = pair[1]
                if src_city == dst_city:
                    continue            
                print_x("*****[Scheduler=%s, Vendor=%s] From City: %s - To City: %s *****" % (self._scheduler_id, self._vendor, src_city, dst_city))
                query_url = (self._ahataxis_query_url %  ('one-way', src_city, dst_city))
                date_url = (self._ahataxis_date_url % (trip_date,'09:00'))
                this_url = self._ahataxis_domain_url + query_url + date_url
                print_x(this_url)
                metadata = {'src_city': src_city, 'dst_city': dst_city, 'trip_date': trip_date, 'url': this_url }
                urls.append(metadata)
                    
        return urls


    def get_onewaycab_urls(self, selected_days):
        normalized_src_cities = self.normalize_onewaycab_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_onewaycab_city_names(self._dst_cities)

        urls = []
        for trip_date in self._timeDecorator.get_oneway_date_range('onewaycab', selected_days):
            for pair in zip(normalized_src_cities, normalized_dst_cities):
                src_city = pair[0]
                dst_city = pair[1]
                if src_city == dst_city:
                    continue
                print_x("*****[Scheduler=%s, Vendor=%s] From City: %s - To City: %s *****" % (self._scheduler_id, self._vendor, src_city, dst_city))
                query_url = (self._onewaycab_query_url %  (src_city, dst_city))

                this_url = self._onewaycab_domain_url + query_url 
                metadata = {'src_city': src_city, 'dst_city': dst_city,'trip_date':trip_date, 'url': this_url }
                print_x(this_url)
                urls.append(metadata)
        return urls

    
    def get_wiwigo_urls(self, selected_days):
        normalized_src_cities = self.normalize_wiwigo_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_wiwigo_city_names(self._dst_cities)

        urls = []
        for trip_date in self._timeDecorator.get_oneway_date_range('wiwigo', selected_days):
            for pair in zip(normalized_src_cities, normalized_dst_cities):
                src_city = pair[0]
                dst_city = pair[1]
                if src_city == dst_city:
                    continue
                print_x("*****[Scheduler=%s, Vendor=%s] From City: %s - To City: %s *****" % (self._scheduler_id, self._vendor, src_city, dst_city))
                query_url = (self._wiwigo_query_url %  (src_city, dst_city))
                
                date_url = (self._wiwigo_date_url % trip_date)
                this_url = self._wiwigo_domain_url + query_url + date_url
                metadata = {'src_city': src_city, 'dst_city': dst_city, 'trip_date': trip_date, 'url': this_url }
                print_x(this_url)
                urls.append(metadata)
        return urls
        
        
        
    def get_getmecab_urls(self, selected_days):
        normalized_src_cities = self.normalize_getmecab_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_getmecab_city_names(self._dst_cities)

        urls = []
        for trip_date in self._timeDecorator.get_oneway_date_range('getmecab', selected_days):
            for pair in zip(normalized_src_cities, normalized_dst_cities):
                src_city = pair[0]
                dst_city = pair[1]
                if src_city == dst_city:
                    continue
                print_x("*****[Scheduler=%s, Vendor=%s] From City: %s - To City: %s *****" % (self._scheduler_id, self._vendor, src_city, dst_city))
                query_url = (self._getmecab_query_url %  (src_city, dst_city))
                
                #date_url = (self._getmecab_date_url % trip_date)
                this_url = self._getmecab_domain_url + query_url
                metadata = {'src_city': src_city, 'dst_city': dst_city,'trip_date':trip_date, 'url': this_url }
                print_x(this_url)
                urls.append(metadata)
        return urls
            
    def get_mytaxiindia_urls(self, selected_days):
    
        '''
        data = {
                'trip_type'     : 'One Way Trip',
                'OS_From'       : 'New Delhi',
                'f_cit_val'     : '82',
                'f_cit_name'    : 'New Delhi',
                'OS_To'         : 'Agra',
                't_cit_val'     : '352',
                't_cit_name'    : 'Agra',
                'osDate'        : '27/07/2018',
                'duration'      : '27/07/2018'
            }
        '''
        
        normalized_src_cities = self.normalize_mytaxiindia_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_mytaxiindia_city_names(self._dst_cities)

        df = self.Instance._mytaxiindia_df.copy()
        
        urls = []
        for trip_date in self._timeDecorator.get_oneway_date_range('mytaxiindia', selected_days):
            for pair in zip(normalized_src_cities, normalized_dst_cities):
                src_city = pair[0]
                dst_city = pair[1]
                if src_city == dst_city:
                    continue
                
                src_df = df[df['city'] == src_city]
                if (src_df.empty):
                    continue
                dest_df = df[df['city'] == dst_city]
                if (dest_df.empty):
                    continue
                
                print_x("*****[Scheduler=%s, Vendor=%s] From City: %s - To City: %s *****" % (self._scheduler_id, self._vendor, src_city, dst_city))
                src_value = ''
                src_label = ''
                for src_row in src_df.itertuples():    
                    src_value = src_row.value
                    src_label = src_row.label
                    
                dst_value = ''
                dst_label = ''
                for dst_row in dest_df.itertuples():
                    dst_value = dst_row.value
                    dst_label = dst_row.label
                
                query_url = self._mytaxiindia_domain_url

                formdata = {'trip_type':'One Way Trip',\
                        'OS_From':src_label, 'f_cit_val':src_value, 'f_cit_name':src_label,\
                        'OS_To':dst_label, 't_cit_val':dst_value, 't_cit_name':dst_label,\
                        'osDate':trip_date, 'duration':trip_date}
                metadata = {'src_city': src_city, 'dst_city': dst_city, 'trip_date': trip_date, 'url': query_url, 'formdata':formdata }
                print_x("query_url=%s, formdata=%s" % (query_url, formdata))
                urls.append(metadata)

        return urls

    
    def get_hippocabs_urls(self,selected_days):
        '''
        
        Form Data: view URL encoded
            drp_start_city: Chandigarh
            drp_end_city: Manali
            txt_pickup: Chandigarh, India
            txt_dropoff: Manali, Himachal Pradesh, India
            txt_datetime: 04/03/19
            drp_time: 09:00 AM
            pas_contact1: 9876543210        
        
        '''
        
        normalized_src_cities = self.normalize_hippocabs_city_names(self._src_cities)
        normalized_dst_cities = self.normalize_hippocabs_city_names(self._dst_cities)

        df = self.Instance._hippocabs_df.copy()
        
        print('Hippocabs Dataframe: ', df)
        urls = []
        for trip_date in self._timeDecorator.get_oneway_date_range('hippocabs', selected_days):
            for pair in zip(normalized_src_cities, normalized_dst_cities):
                src_city = pair[0]
                dst_city = pair[1]
                if src_city == dst_city:
                    continue
                 
                src_df = df[df['city'] == src_city]
                if (src_df.empty):
                    continue
                dest_df = df[df['city'] == dst_city]
                if (dest_df.empty):
                    continue
                
                print("*****[Scheduler=%s, Vendor=%s] From City: %s - To City: %s, Trip Data: %s*****" % (self._scheduler_id, self._vendor, src_city, dst_city, trip_date))
                #src_value = ''
                src_label = ''
                for src_row in src_df.itertuples():    
                    src_label = src_row.city
                    #src_value = self.get_hippo_pickup_dropoff(src_label)
                    
                #dst_value = ''
                dst_label = ''
                for dst_row in dest_df.itertuples():
                    dst_label = dst_row.city
                    #dst_value = self.get_hippo_pickup_dropoff(dst_label)
                
                query_url = self._hippocabs_domain_url
                mobile_no= self.gen_phone()
                # formdata = {'trip_type':'One Way Trip',\
                        # 'OS_From':src_label, 'f_cit_val':src_value, 'f_cit_name':src_label,\
                        # 'OS_To':dst_label, 't_cit_val':dst_value, 't_cit_name':dst_label,\
                        # 'osDate':trip_date, 'duration':trip_date}
                
                '''
                formdata = {
                        'textbox-country':src_label, \
                        'textbox-city':dst_label,\
                        'pickup-head':src_label, \
                        'dropoff-head':dst_label,\
                        'date-textbox':trip_date, 'time-textbox':"09:00 AM",'txt_contact_coupon':mobile_no}
                '''
                formdata = {
                        'drp_start_city':src_label, \
                        'drp_end_city':dst_label,\
                        'txt_pickup':src_label, \
                        'txt_dropoff':dst_label,\
                        'txt_datetime':trip_date, 
                        'drp_time':"09:00 AM",
                        'pas_contact1':mobile_no}
                        
                metadata = {'src_city': src_city, 'dst_city': dst_city, 'trip_date': trip_date, 'url': query_url, 'formdata':formdata }
                print("query_url=%s, formdata=%s" % (query_url, formdata))
                urls.append(metadata)

        return urls
        



