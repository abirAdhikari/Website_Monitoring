# Author: AADHIKARI 5/31/2018
# https://doc.scrapy.org/en/0.10.3/topics/selectors.html

from datetime import datetime, date, timedelta, time
START_DATE_OFFSET = 2
END_DATE_OFFSET = 2
TOTAL_TRIP_DAYS = 0 # 0 for oneway, > 0 for roundtrip

class TimeDecorator(object):
    def __init__(self, in_start_date=None, in_end_date=None, in_start_time=None, in_end_time=None):
    
        if in_start_date==None or in_end_date==None:
            self._start_date    =   date.today() + timedelta(START_DATE_OFFSET)
            self._end_date      =   date.today() + timedelta(START_DATE_OFFSET+END_DATE_OFFSET) 
        else:
            self._start_date    =   datetime.strptime(in_start_date, '%Y-%m-%d').date()
            self._end_date      =   datetime.strptime(in_end_date, '%Y-%m-%d').date()
            
        if in_start_time==None or in_end_time==None:
            self._start_time    =   '09:00'
            self._end_time      =   '20:00'
        else:
            self._start_time    =   in_start_time
            self._end_time      =   in_end_time
            
        self._day_index = {'Mon':1, 'Tue':2, 'Wed':3, 'Thur':4, 'Fri':5, 'Sat':6, 'Sun':7}
        
    
    def daterange(self, start_date, end_date, selected_days):
        selected_days_indices = []
        for x in selected_days:
            selected_days_indices.append(self._day_index[x])
        
        for n in range(int ((end_date - start_date).days)):
            current_date = start_date + timedelta(n)
            if current_date.isoweekday() in selected_days_indices:
                yield current_date  
         
    def get_time_decorator(self, hint):
        return {'start_date'       :self._start_date, 
                'end_date'         :self._end_date,
                'start_time'       :self._start_time,
                'end_time'         :self._end_time }
            
    def get_oneway_date_range(self, hint, selected_days):
        date_range=list()
        if hint == 'wiwigo' or hint == 'onewaycab' or hint == 'ahataxis':
            for this_date in self.daterange(self._start_date, self._end_date, selected_days):
                in_date = this_date.strftime("%Y-%m-%d");
                date_range.append(in_date)
        elif hint == 'makemytrip':
            for this_date in self.daterange(self._start_date, self._end_date, selected_days):
                in_date = this_date.strftime("%d-%m-%Y");
                date_range.append(in_date)
        elif hint == 'mytaxiindia':
            for this_date in self.daterange(self._start_date, self._end_date, selected_days):
                in_date = this_date.strftime("%d/%m/%Y");
                date_range.append(in_date)
        elif hint == 'hippocabs':
            for this_date in self.daterange(self._start_date, self._end_date, selected_days):
                in_date = this_date.strftime("%m/%d/%Y");
                date_range.append(in_date)
        return date_range
    
    
    def normalize_date_for_database(in_date):
        date_object = datetime.strptime(in_date, '%d-%m-%Y')
        return date_object.strftime("%Y-%m-%d")
        