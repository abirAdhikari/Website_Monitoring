# Author: AADHIKARI - 06/03/2018

import os 
import sys 
sys.path.append('.')
import logging

from sqlite3 import dbapi2 as sqlite

class CompetitiveDataPipeline(object):
    def __init__(self):
        self.open_database_connection()
        pass

    def process_item(self, item, spider):
        # If SQL lite is opened from spider_opened() or closed from spider_closed() then we get below messages
        '''
        ProgrammingError: SQLite objects created in a thread can only be used in that 
        same thread.The object was created in thread id 23508 and this is thread id 
        22640
        '''
        self.open_database_connection()
        item = self.insert_to_database(item)
        self.close_database_connection()
        return item
        
    def spider_opened(self, spider):
        #
        #self.open_database_connection()
        pass
        
    def spider_closed(self, spider):
        #
        #self.close_database_connection()
        pass
        
    def handle_error(self, e):
        logging.log(logging.ERROR, e)
    
    def open_database_connection(self):
        logging.log(logging.INFO, "CompetitiveDataPipeline::spider_opened(#####): opening database connection")
        #self.connection.close()
        self.connection = sqlite.connect('.\\spiders\\sqlDb\\competitiondatabase.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS competitiondata '\
                    '(unique_id VARCHAR PRIMARY KEY,'\
                    'url_md5 VARCHAR,'\
                    'collection_date DATETIME,'\
                    'pickup_date DATETIME,'\
                    'drop_date DATETIME,'\
                    'pickup_time DATETIME,'\
                    'drop_time DATETIME,'\
                    'trip_type VARCHAR(10),'\
                    'vendor VARCHAR(20),'\
                    'src_city VARCHAR(20),'\
                    'dst_city VARCHAR(20),'\
                    'cab_type VARCHAR(20),'\
                    'normalized_cab_type VARCHAR(20),'\
                    'cab_name VARCHAR(20),'\
                    'pax_count INTEGER,'\
                    'markup_price INTEGER,'\
                    'base_price INTEGER,'\
                    'toll INTEGER,'\
                    'toll_included BOOL,'\
                    'gst INTEGER,'\
                    'gst_included BOOL,'\
                    'free_cancelation BOOL,'\
                    'cancellation_charge INTEGER,'\
                    'coupon INTEGER,'\
                    'poll_priority VARCHAR(20),'\
                    'url VARCHAR(1024))')
        logging.log(logging.INFO, "CompetitiveDataPipeline::spider_opened(#####):  db=competitiondatabase opened")
    
    def close_database_connection(self):
        self.connection.close()
        logging.log(logging.INFO, "CompetitiveDataPipeline::spider_closed(#####): db=competitiondatabase closed")
        
    def insert_to_database(self, item):
        logging.log(logging.INFO, "CompetitiveDataPipeline::insert_to_database((#####):): storing to database")
        self.cursor.execute("select * from competitiondata where unique_id=?", item.get('unique_id')[0])
        result = self.cursor.fetchone()
        if result:
            logging.log(logging.INFO, "CompetitiveDataPipeline::insert_to_database((#####):): Item already in database: %s" % item)
        else:
            self.cursor.execute(
                'REPLACE INTO competitiondata ('\
                    'unique_id,'\
                    'url_md5,'\
                    'collection_date,'\
                    'pickup_date,'\
                    'drop_date,'\
                    'pickup_time,'\
                    'drop_time,'\
                    'trip_type,'\
                    'vendor,'\
                    'src_city,'\
                    'dst_city,'\
                    'cab_type,'\
                    'normalized_cab_type,'\
                    'cab_name,'\
                    'pax_count,'\
                    'markup_price,'\
                    'base_price,'\
                    'toll,'\
                    'toll_included,'\
                    'gst,'\
                    'gst_included,'\
                    'free_cancelation,'\
                    'cancellation_charge,'\
                    'coupon,'\
                    'poll_priority,'\
                    'url) '\
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                    (   item.get('unique_id'),
                        item.get('url_md5'),
                        item.get('collection_date'),
                        item.get('pickup_date'),
                        item.get('drop_date', 0),
                        item.get('pickup_time', 0),
                        item.get('drop_time', 0),
                        item.get('trip_type'),
                        item.get('vendor'),
                        item.get('src_city'),
                        item.get('dst_city'),
                        item.get('cab_type'),
                        item.get('normalized_cab_type'),
                        item.get('cab_name'),
                        item.get('pax_count'),
                        item.get('markup_price'),
                        item.get('base_price'),
                        item.get('toll', 0),
                        item.get('toll_included', False),
                        item.get('gst', 0),
                        item.get('gst_included', False),
                        item.get('free_cancelation', 0),
                        item.get('cancellation_charge', False),
                        item.get('coupon', 0),
                        item.get('poll_priority'),
                        item.get('url')))

            self.connection.commit()
            
            print(item)

            logging.log(logging.INFO, "CompetitiveDataPipeline::insert_to_database((#####):): Item stored : %s" % item)
        return item
    
    