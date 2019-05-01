# AADHIKARI: 7/27/2018 : first cut
import os 
import sys 
import logging
from collections import defaultdict
from datetime import datetime, timedelta, date

from apscheduler.schedulers.background import BackgroundScheduler

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor

from crochet import setup
setup()

from urlgenerator import UrlGenerator
from timedecorator import TimeDecorator


def print_x(msg):
    print(msg)
    pass

class HawkeyeVendorData():
    def __init__(self, schedular_id, vendor, urls, batch_size):
        total_urls = len(urls)
        self._schedular_id  = schedular_id
        self._vendor_id     = vendor
        self._total         = total_urls
        self._successful    = 0
        self._error         = 0
        self._batch_size    = batch_size
        self._pending       = total_urls
        self._urls          = urls
    
    def get_current_urls_set(self):
        if self._pending == 0:
            return []
        
        start_index = self._successful + self._error
        end_index = start_index + self._batch_size
        
        urls = []
        if end_index < self._total:
            urls = self._urls[start_index:end_index]
        else:
            urls = self._urls[start_index:]
        
        print ("Vendor %s, start_index = %s, end_index = %s, len(url) = %s, len(batch_urls) = %s" %\
            (self._vendor_id, start_index, end_index, len(self._urls), len(urls)))
        
        return urls
        
    def executing(self):
        if self._pending == 0:
            return
        self._pending = self._pending - 1
    
    def success(self):
        if self._pending == 0:
            return
        self._successful = self._successful + 1 
        
    def error(self):
        if self._pending == 0:
            return
        self._error = self._error + 1 
    
    def batch_finished(self):
        if self._pending == 0:
            return True
        if (self._total - self._pending) %  self._batch_size == 0:
            return True
        return False
    
    def is_any_pending(self):
        if self._pending == 0:
            return False
        return True

class HawkeyeTaskData():
    def __init__(self, schedular_id, params):
        print_x ("<<<<<>>>> %s, %s" % (schedular_id, params))
        self._schedular_id          = schedular_id
        
        self.in_scheduler_id    = str(params['in_scheduler_id'])            
        self._poll_dates_start  = str(params['in_poll_dates_start'])
        self._poll_dates_end    = str(params['in_poll_dates_end'])     
        self._batch_size        = int(params['in_batch_size'])      
        self._poll_frequency    = params['in_poll_frequency']
        self._selected_days     = params['in_select_days']        
        self._selected_vendors  = params['in_select_vendors'] 
        self._progress_data     = defaultdict(str)
        vendor_counts           = len(self._selected_vendors)
        for i in range (0, vendor_counts):
            vendor = self._selected_vendors[i].lower()
            dtimeDecorator = TimeDecorator(in_start_date=self._poll_dates_start, in_end_date=self._poll_dates_end)
            urlGenerator = UrlGenerator(schedular_id, vendor, dtimeDecorator, True)
            urls = urlGenerator.get_filtered_urls(self._selected_days)
            total_urls = len(urls)
            self._progress_data[vendor] = HawkeyeVendorData(schedular_id, vendor, urls, self._batch_size)
    
    def get_current_urls_set(self, vendor):
        return self._progress_data[vendor].get_current_urls_set()
        
    def executing(self, vendor):
        self._progress_data[vendor].executing()
        
    def success(self, vendor):
        self._progress_data[vendor].success() 
        
    def error(self, vendor):
        return self._progress_data[vendor].error() 
    
    def batch_finished(self, vendor):
        return self._progress_data[vendor].batch_finished()
    
class HawkeyeTasks():
    '''Singelton Start''' 
    class __HawkeyeTasks:
        def __init__(self):
            self._global_params_dict = defaultdict(str)
            
        def add(self, schedular_id, params):
            self._global_params_dict[schedular_id] = HawkeyeTaskData(schedular_id, params)
            return params
            
        def get(self, schedular_id):
            if schedular_id in self._global_params_dict:
                return self._global_params_dict[schedular_id]
            return None
            
        def remove(self, schedular_id):
            if schedular_id in self._global_params_dict:
                params = self._global_params_dict[schedular_id]
                self._global_params_dict.pop(schedular_id)
                logging.log(logging.INFO, "HawkeyeTasks::remove(*****): Removed params: %s" % (schedular_id))
            
    '''Singelton End'''
    
    Instance = None
    
    def __init__(self):
    
        if not HawkeyeTasks.Instance:
            HawkeyeTasks.Instance = HawkeyeTasks.__HawkeyeTasks()

class HawkeyeScheduler():

    '''Singelton Start''' 
    class __HawkeyeScheduler:
        def __init__(self):
            self._global_scheduler_dict = defaultdict(str)
            
        def add(self, schedular_id):
            scheduler = BackgroundScheduler()
            self._global_scheduler_dict[schedular_id] = scheduler
            return scheduler
            
        def get(self, schedular_id):
            if schedular_id in self._global_scheduler_dict:
                return self._global_scheduler_dict[schedular_id]
            return None
            
        def remove(self, schedular_id):
            if schedular_id in self._global_scheduler_dict:
                scheduler = self._global_scheduler_dict[schedular_id]
                self._global_scheduler_dict.pop(schedular_id)
                logging.log(logging.INFO, "__HawkeyeScheduler::remove(*****): Removed scheduler: %s" % (schedular_id))
            
    '''Singelton End'''
    
    Instance = None
    
    def __init__(self, schedular_id, context, config):
    
        if not HawkeyeScheduler.Instance:
            HawkeyeScheduler.Instance = HawkeyeScheduler.__HawkeyeScheduler()
        
        self._scheduler = HawkeyeScheduler.Instance.get(schedular_id)
        self.schedular_id = schedular_id
        if context == 'START':
            if self._scheduler == None: 
                self._scheduler = HawkeyeScheduler.Instance.add(schedular_id)
                HawkeyeTasks().Instance.add(schedular_id, config)
                self._isRunning = False
            else:
                self._isRunning = True
        elif context == 'STOP':
            if self._scheduler == None: 
                self._isRunning = False
            else:
                self._isRunning = True
        poll_interval = config['in_poll_frequency'].split()
        if poll_interval[1] == 'seconds':
            self._poll_interval = int(poll_interval[0])
        elif poll_interval[1] == 'minutes':
            self._poll_interval = int(poll_interval[0]) * 60
        elif poll_interval[1] == 'hours':
            self._poll_interval = int(poll_interval[0]) * 60 * 60
        elif poll_interval[1] == 'days':
            self._poll_interval = int(poll_interval[0]) * 60 * 60 * 24
                
        self._context = context
        self._config = config
        self._schedular_id = schedular_id
    
    def start(self):
        if self._isRunning == False:
            self._isRunning = True
            # run now
            # run perodically too
            self._scheduler.add_job(self.run_crawl_runner, 'interval', seconds=self._poll_interval, next_run_time=datetime.now())
            self._scheduler.start()
            logging.log(logging.INFO, "HawkeyeScheduler::start(*****): Scheduler %s STARTED" % (self._schedular_id))
            print_x("HawkeyeScheduler::start(*****): Scheduler %s STARTED" % (self._schedular_id))
        else:
            logging.log(logging.INFO, "HawkeyeScheduler::start(*****): Scheduler %s ALREADY RUNNING " % (self._schedular_id))
            print_x ("HawkeyeScheduler::start(*****): Scheduler %s ALREADY RUNNING " % (self._schedular_id))
            
    def stop(self):
        if self._isRunning == False:
            logging.log(logging.INFO, "HawkeyeScheduler::stop(*****): Scheduler %s IS NOT RUNNING " % (self._schedular_id))
            print_x ("HawkeyeScheduler::stop(*****): Scheduler %s IS NOT RUNNING " % (self._schedular_id))
        else:   
            self._scheduler.shutdown()
            self._isRunning = False
            HawkeyeScheduler.Instance.remove(self._schedular_id)
            HawkeyeTasks().Instance.remove(self._schedular_id)
            logging.log(logging.INFO, "HawkeyeScheduler::stop(*****): Scheduler %s STOPPED" % (self._schedular_id))
            print_x("HawkeyeScheduler::stop(*****): Scheduler %s STOPPED" % (self._schedular_id))       
        
    
    def dummy_run(self):
        logging.log(logging.INFO, "HawkeyeScheduler::run(*****)")
        hawkeyetaskdata = HawkeyeTasks().Instance.get(self._schedular_id)
        any_pending = True
        for vendor, progress in hawkeyetaskdata._progress_data.items():
            print_x ('%s, %s' % (vendor, progress))
            progress.success()
            any_pending |= progress.is_any_pending()
        
        if any_pending == False:
            stop()
        print_x ("%s: HawkeyeScheduler::run(*****) scheduler_id=%s, config=%s" % (datetime.now(), self._schedular_id, self._config))
    
    # 8/7/2018: DOESN'T WORK, keep getting 'twisted.internet.error.ReactorNotRestartable' after each cycle
    # TRYING -  https://stackoverflow.com/questions/41495052/scrapy-reactor-not-restartable/43661172
    '''
        This is what helped for me to win the battle against ReactorNotRestartable error: last answer from the author of the question
        0) pip install crochet
        1) import from crochet import setup
        2) setup() - at the top of the file
        3) remove 2 lines:
        a) d.addBoth(lambda _: reactor.stop())
        b) reactor.run()
    '''
    def run_crawl_runner(self):
        logging.log(logging.INFO, "HawkeyeScheduler::run_crawl_runner(*****) Enter ")
        hawkeyetaskdata = HawkeyeTasks().Instance.get(self._schedular_id)
        runnable_spiders = hawkeyetaskdata._selected_vendors
        if len(runnable_spiders) == 0:
            logging.log(logging.INFO, "HawkeyeScheduler::run_crawl_runner(*****) Exit (No vendor selected)")
            return
        spids = []
        for s in runnable_spiders:
            spids.append(s.lower())
        setting = get_project_settings()
        runner = CrawlerRunner(setting)
        loader = runner.spider_loader
        #if len(spids) == 0:
        #   spids = loader.list()
        spiders = [loader.load(_)
                   for _ in filter(lambda __: __ in loader.list(),
                                   spids)]
        if not spiders:
            return
        #random.shuffle(spiders)
        for __ in spiders:
            runner.crawl(__, scheduler_id=self._schedular_id)
        d = runner.join()
        #d.addBoth(lambda _: reactor.stop())
        #logging.log(logging.INFO, 'Crawl Reator Starting ...')
        #reactor.run(installSignalHandlers=False)
        #reactor.run()
        #logging.log(logging.INFO, 'Crawl Reator Stopped ...')
        print_x ("%s: HawkeyeScheduler::run_crawl_runner(*****) scheduler_id=%s, config=%s" % (datetime.now(), self._schedular_id, self._config))
    
    
    # DOESN'T WORK
    # gives error: 'ValueError: signal only works in main thread'
    def run_crawler_process(self):
        logging.log(logging.INFO, "HawkeyeScheduler::run_crawler_process(*****) Enter ")
        hawkeyetaskdata = HawkeyeTasks().Instance.get(self._schedular_id)
        runnable_spiders = hawkeyetaskdata._selected_vendors
        if len(runnable_spiders) == 0:
            logging.log(logging.INFO, "HawkeyeScheduler::run_crawler_process(*****) Exit (No vendor selected)")
            return
        spids = []
        for s in runnable_spiders:
            spids.append(s.lower())
        setting = CrawlerProcess(get_project_settings())
        process = CrawlerProcess(setting)
        loader = runner.spider_loader
        #if len(spids) == 0:
        #   spids = loader.list()
        spiders = [loader.load(_)
                   for _ in filter(lambda __: __ in loader.list(),
                                   spids)]
        if not spiders:
            return
        #random.shuffle(spiders)
        for __ in spiders:
            process.crawl(spider_name, priority=self._schedular_id)
        print_x ("%s: HawkeyeScheduler::run_crawler_process(*****) scheduler_id=%s, config=%s" % (datetime.now(), self._schedular_id, self._config))
    