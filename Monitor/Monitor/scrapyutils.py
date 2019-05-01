# Author: AADHIKARI 5/31/2018
# https://doc.scrapy.org/en/0.10.3/topics/selectors.html

from datetime import datetime
from datetime import date
from datetime import timedelta
import pandas
import io
import hashlib

'''
SELECT * FROM competitiondata where cab_type = "AC TEMPO TRAVELLER"
UPDATE competitiondata SET normalized_cab_type = 'AC TEMPO TRAVELLER' where cab_type = "AC TEMPO TRAVELLER"
'''

class ScrapyUtils(object):
    
    def make_clickable(val):
        # target _blank to open new window
        return '<a target="_blank" href="{}">Verify</a>'.format(val)
        
    def custom_header():
        custom_header_empty = {}
        custom_header_mozila = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'}
        custom_header_apple = {'User-Agent': 'AppleWebKit/537.36 (KHTML, like Gecko)'}
        custom_header_chrome = {'User-Agent': 'Chrome/42.0.2311.90 Safari/537.36'}
        return custom_header_mozila
    
    def use_url_generator():
        return True
    
    def __init__(self):
        self._log_to_csv = False
        pass
    
    def initialize_competitive_data(competitiveDataItem):
        pass
        
    def create_file_and_write_headers(meta):
        _output_file_name = '.\\spiders\\data\\' + meta + str(datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]) + '.csv'
        _file = open(_output_file_name, 'w')
        _file.write("TripDate, RecordDate, Vendor, Source, Destination, CarType, CarName, Passengers, Price\n")
        _file.close()
        return _output_file_name
        
    def write_to_file(_output_file_name, trip_date, record_date, vendor, source, destination, cartype, carname, passengers, price):
        
        pass
        '''
        for remove in [':', ',']:
            cartype = cartype.replace(remove,' ')
            carname = carname.replace(remove,' ')
            price = price.replace(remove, '')
            
        _output = trip_date+","+record_date+","+ vendor+","+source+","+destination+","+cartype+","+carname+","+passengers+","+price +"\n"
        _file = open(_output_file_name, 'a')
        _file.write(_output)
        _file.close()
        '''
    
    def wiwigo_get_cab_type_from_cab_name(hint):
        cab_type = 'Unknown'
        if 'Ritz / Indica / Similar' in hint:
            cab_type = 'AC HATCHBACK'
        if 'Swift Dzire / Toyota Etios / Similar' in hint:
            cab_type = 'AC SEDAN'
        elif 'Toyota Innova / Xylo / Similar' in hint:
            cab_type = 'AC SUV'     
        elif 'Force Tempo Traveller-12 Seater' in hint:
            cab_type = 'AC TEMPO TRAVELLER'
        return cab_type
    
    def mytaxiindia_get_cab_type_from_cab_name(hint):
        cab_type = 'Unknown'
        if 'Indica' in hint or 'Ritz' in hint:
            cab_type = 'AC HATCHBACK'
        if 'Dzire' in hint or 'Etios' in hint:
            cab_type = 'AC SEDAN'
        elif 'Innova' in hint or 'Xylo' in hint:
            cab_type = 'AC SUV'     
        elif 'Tempo Traveler 12 Seater' in hint:
            cab_type = 'AC TEMPO TRAVELLER'
        return cab_type
    
    def mytaxiindia_remove_junk_from_cab_name(hint):
        cab_type = 'Unknown'
        if 'Indica' in hint:
            cab_type = 'Indica Or Equivalent'
        if 'Dzire' in hint:
            cab_type = 'Dzire Or Equivalent'
        elif 'Innova' in hint:
            cab_type = 'Innova Or Equivalent'       
        elif 'Tempo Traveler 12 Seater' in hint:
            cab_type = 'Tempo Traveler 12 Seater'
        return cab_type
        
    def mytaxiindia_normalize_date(in_date):
        date_object = datetime.strptime(in_date, '%d/%m/%Y')
        return date_object.strftime("%Y-%m-%d")
    
    def hippocabs_get_cab_type_from_cab_name(hint):
        cab_type = 'Unknown'
        if 'Xcent, Amaze' in hint:
            cab_type = 'AC SEDAN'
        if 'Xylo, Ertiga' in hint:
            cab_type = 'AC SUV'
        elif 'Dzire/Etios Only' in hint:
            cab_type = 'AC SEDAN'       
        elif 'Innova Only' in hint:
            cab_type = 'AC SUV'
        if 'only' in hint:
            cab_type = 'ASSURED ' + cab_type            
        return cab_type
    
    def hippocabs_normalize_date(in_date):
        date_object = datetime.strptime(in_date, '%d/%m/%Y')
        return date_object.strftime("%Y-%m-%d")
        
    def get_cab_type_from_cab_name(hint):
        cab_type = ''
        if 'Ritz' in hint or 'Indica' in hint:
            cab_type = 'AC HATCHBACK'
        elif 'Dzire' in hint or 'Etios' in hint:
            cab_type = 'AC SEDAN'
        elif 'Innova' in hint or 'Xylo' in hint:
            cab_type = 'AC SUV'
        elif 'Tempo Traveller' in hint:
            cab_type = 'AC TEMP TRAVELLER'
        return cab_type
    
    def get_cab_name_from_cab_type(hint):
        cab_name = ''
        hint = hint.lower()
        if 'hatchback' in hint:
            cab_name = 'Indica Vista, Suzuki Swift, Hyundai Eon etc'
        elif 'sedan' in hint:
            cab_name = 'Tata Indigo, Swift Dzire, Toyota Etios etc'
        elif 'suv' in hint:
            cab_name = 'Toyota Innova, Xylo'
        elif 'temp traveller' in hint:
            cab_name = 'Tempo Traveller'
        return cab_name
    
    def get_pax_count_from_cab_type(hint):
        hint = hint.lower()
        pax_count = '4 Passengers' 
        if 'hatchback' in hint:
            pax_count = '4 Passengers'
        elif 'sedan' in hint:
            pax_count = '4 Passengers'
        elif 'suv' in hint:
            pax_count = '6 Passengers'
        elif 'traveller' in hint:
            pax_count = '12 Passengers'
        return str(pax_count)
    
    def normalize_cab_type(hint):
        hint = hint.lower()
        cab_type = 'Unknown' 
        if 'hatchback' in hint or 'economy' in hint:
            cab_type = 'AC HATCHBACK'
        elif 'sedan' in hint or 'comfort' in hint or 'dzire' in hint:
            cab_type = 'AC SEDAN'
        elif 'premium' in hint or 'suv' in hint or 'innova' in hint:
            cab_type = 'AC SUV'
        elif 'innova' in hint:
            cab_type = 'AC INNOVA'
        elif 'traveller' in hint:
            cab_type = 'AC TEMPO TRAVELLER'
            
        if 'assured' in hint:
            cab_type = 'ASSURED ' + cab_type
        return str(cab_type)

    def normalize_ahataxi_cab_type(input):
        # AHA Economy, AHA Comfort, AHA Premium, AHA Assured Innova
        return input.replace('AHA', 'AC').upper()
    
    def write_to_file_v2(filename, content):
        f = open(filename, 'w')
        f.write(str(content))
        f.close()
    
    def write_to_io_file(filename, content):
        with io.open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    
    def get_unique_key(meta, cab_type):
        m=hashlib.md5(bytes(str(meta),"ascii"))   # python 3
        url_md5 = m.hexdigest()
        unique_id = url_md5 + '_' + str(date.today()) + '_' + cab_type.strip(' ').replace(':', '').replace(' ', '_')
        return unique_id, url_md5
    
        
    def create_dataframe():
        df = pandas.DataFrame(columns=['TripDate', 'RecordDate', 'Vendor', 'Source', 'Destination', 'CarType', 'CarName', 'Passengers', 'Price'])
        return df
    def write_dataframes(df, trip_date, record_date, vendor, source, destination, cartype, carname, passengers, price):
        df.append({
             'TripDate'     : trip_date,
             'RecordDate'   : record_date,
             'Vendor'       : vendor,
             'Source'       : source,
             'Destination'  : destination,
             'CarType'      : cartype,
             'CarName'      : carname,
             'Passengers'   : passangers,
             'Price'        : price,             
              }, ignore_index=True)
        print(trip_date, record_date, vendor, source, destination, cartype, carname, passangers, price)