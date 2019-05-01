# Author: AADHIKARI 06/12/2018

import os 
import sys 
import dash
import pandas as pd
import numpy as np
import plotly
import logging
import sqlite3
from datetime import datetime, timedelta, date


db_file = os.getcwd() + '\\spiders\\sql\\competition.db'

class CompetitiveData(object):

    class __CompetitiveData(object):
    
        def __init__(self):
            logging.log(logging.INFO, '__CompetitiveData::__init__()')
            conn = sqlite3.connect(db_file)
            logging.log(logging.INFO, '__CompetitiveData()::__init__ Gettting data from datebase')
            self._DF_COMPETITION = pd.read_sql_query("select * from competitiondata;", conn)
            conn.close()
            self.__rename_columns()
            
        def __refresh_from_database(self, in_start_date, in_end_date):
            logging.log(logging.INFO, '__CompetitiveData::__refresh_from_database()')
            conn = sqlite3.connect(db_file)
            logging.log(logging.INFO, '__CompetitiveData::__refresh_from_database() Refreshing data from datebase')
            query = ''
            if in_start_date == None or in_end_date == None:
                query = 'select * from competitiondata;'
            else:
                query = 'select * from competitiondata where pickup_date >= \'' + str(in_start_date) + '\' and pickup_date <= \''+ str(in_end_date) +'\';'
            logging.log(logging.INFO, '__CompetitiveData::__refresh_from_database() Run SQL Query = %s' % query)
            self._DF_COMPETITION = pd.read_sql_query(query, conn)
            conn.close()
            print (query)
            if len(self._DF_COMPETITION) == 0:
                return self._DF_COMPETITION
            self.__rename_columns()
            return self._DF_COMPETITION
        
        def __rename_columns(self):
            #self._DF_COMPETITION['total_price'] = self._DF_COMPETITION.apply(lambda row: row.base_price + row.toll + row.gst - row.coupon, axis=1)
            self._DF_COMPETITION['total_price'] = self._DF_COMPETITION['base_price']
            self._DF_COMPETITION.sort_values(by=['pickup_date', 'src_city', 'dst_city', 'total_price', 'vendor', 'normalized_cab_type'], inplace=True)
            self._DF_COMPETITION.reset_index(inplace=True)
            self._DF_COMPETITION['Index'] = self._DF_COMPETITION.index
            self._DF_COMPETITION.rename(inplace=True, 
                    columns={
                                'collection_date'   : 'Collection Date', 
                                'pickup_date'       : 'Pickup Date',
                                'drop_date'         : 'Drop Date',
                                'pickup_time'       : 'Pickup Time',
                                'drop_time'         : 'Drop Time',
                                'trip_type'         : 'Trip Type',
                                'vendor'            : 'Vendor',
                                'src_city'          : 'From City',
                                'dst_city'          : 'To City',
                                'cab_type'          : 'Cab Type',
                                'normalized_cab_type' : 'Normalized Cab Type',
                                'cab_name'          : 'Cab Name',
                                'pax_count'         : 'Pax Count',
                                'total_price'       : 'Total Price',
                                'markup_price'      : 'Markup Price',
                                'base_price'        : 'Base Price',
                                'toll'              : 'Toll',
                                'toll_included'     : 'Toll Included',
                                'gst'               : 'GST',
                                'gst_included'      : 'GST Included',
                                'free_cancelation'  : 'Free Cancelation',
                                'cancellation_charge' : 'Cancellation Charge',
                                'coupon'            : 'Coupon',
                                'poll_priority'     : 'Poll Priority',
                                'url'               : 'URL'
                            })
            self._DF_COMPETITION = self._DF_COMPETITION[
                                ['Index', 
                                'unique_id',
                                'Collection Date', 
                                'Pickup Date',
                                'Drop Date',
                                'Pickup Time',
                                'Drop Time',
                                'Trip Type',
                                'From City',
                                'To City',
                                'Normalized Cab Type',
                                'Vendor',
                                'Total Price',
                                'Markup Price',
                                'Base Price',
                                'Cab Type',
                                'Cab Name',
                                'Pax Count',
                                'Toll',
                                'Toll Included',
                                'GST',
                                'GST Included',
                                'Free Cancelation',
                                'Cancellation Charge',
                                'Coupon',
                                'Poll Priority',
                                'URL'
                                ]]

            self._DF_COMPETITION.drop(['unique_id', 'Pickup Time', 'Drop Time', 'Coupon', 'Cancellation Charge', 'Free Cancelation', 'Markup Price','Toll',
                                'Toll Included',
                                'GST',
                                'GST Included',
                                'Free Cancelation',
                                'Cancellation Charge',
                                'Coupon',], axis = 1, inplace = True)
            self._DF_COMPETITION['Pickup Date'] = pd.to_datetime(self._DF_COMPETITION['Pickup Date'])
                        
            #target _blank to open new window
            def make_clickable(val):
                return '<a target="_blank" href="{}">Verify</a>'.format(val)
            #self._DF_COMPETITION.style.format({'URL': make_clickable})
            
        def __get_lowest_price_per_route(self, in_start_date, in_end_date):
            df_competition = self._DF_COMPETITION.copy()
            
            '''
            Not needed anymore, database query is hooked up
            if in_start_date == None or in_end_date == None:
                pass
            elif in_start_date == in_end_date: # date single
                df_competition = df_competition[(df_competition['Pickup Date'] == in_start_date)]
            else: # range date
                df_competition = df_competition[(df_competition['Pickup Date'] > in_start_date) & (df_competition['Pickup Date'] < in_end_date)]
            '''
            
            #df_competition.drop(['Toll','Toll Included','GST','GST Included','Drop Date'], axis = 1, inplace = True)
            
            '''
            df_competition['Min'] = df_competition.groupby(['Pickup Date', 'From City', 'To City', 'Normalized Cab Type'])['Total Price'].transform('min')
            df_competition['Max'] = df_competition.groupby(['Pickup Date', 'From City', 'To City', 'Normalized Cab Type'])['Total Price'].transform('max')
            df_competition['Avg'] = df_competition.groupby(['Pickup Date', 'From City', 'To City', 'Normalized Cab Type'])['Total Price'].transform('mean')
            df_competition['Avg'] = df_competition['Avg'].astype(np.int64)
            
            df_competition = df_competition.groupby(['Pickup Date', 'From City', 'To City', 'Normalized Cab Type'])['Total Price'].min()
            
            '''
            
            min_indices = df_competition.groupby(['Pickup Date', 'From City', 'To City', 'Normalized Cab Type'])['Total Price'].idxmin
            print(min_indices)
            df_competition = df_competition.loc[min_indices]
            #df_competition.reset_index()
            return df_competition

        
    Instance = None
    
    def singelton_init(self):
        if CompetitiveData.Instance == None:
            logging.log(logging.INFO, 'CompetitiveData::singelton_init Initializing singelton instance')
            CompetitiveData.Instance = CompetitiveData.__CompetitiveData()
            
    def __init__(self):     
        logging.log(logging.INFO, 'CompetitiveData::.__init__()')
        self.singelton_init()
        
    def refresh_from_database(self, in_start_date, in_end_date):
        logging.log(logging.INFO, 'CompetitiveData::refresh_from_database()')
        self.singelton_init()   
        return CompetitiveData.Instance.__refresh_from_database(in_start_date, in_end_date)
        
    def get_records(self):
        logging.log(logging.INFO, 'CompetitiveData::get_records()')
        self.singelton_init()
        return CompetitiveData.Instance._DF_COMPETITION.to_dict('records')

    
    def get_lowest_price_per_route(self, in_start_date, in_end_date):
        logging.log(logging.INFO, 'CompetitiveData::get_lowest_price_per_route()')
        self.singelton_init()   
        CompetitiveData.Instance.__refresh_from_database(in_start_date, in_end_date)
        if len(CompetitiveData.Instance._DF_COMPETITION) == 0:
            return CompetitiveData.Instance._DF_COMPETITION
        return CompetitiveData.Instance.__get_lowest_price_per_route(in_start_date, in_end_date)

    
