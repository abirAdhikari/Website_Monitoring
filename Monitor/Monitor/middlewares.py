# -*- coding: utf-8 -*-
import logging

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.conf import settings
# from settings import PROXIES
# import base64
# from fake_useragent import UserAgent

#logger = logging.getLogger(__name__)


class HawkeyeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class HawkeyeDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


from random import choice
from scrapy import signals
from scrapy.exceptions import NotConfigured

class RotateUserAgentMiddleware(object):
    """Rotate user-agent for each request."""
    def __init__(self, user_agents):
        self.enabled = False
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        user_agents = crawler.settings.get('USER_AGENT_CHOICES', [])

        if not user_agents:
            raise NotConfigured("USER_AGENT_CHOICES not set or empty")

        o = cls(user_agents)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)

        return o

    def spider_opened(self, spider):
        self.enabled = getattr(spider, 'rotate_user_agent', self.enabled)

    def process_request(self, request, spider):
        if not self.enabled or not self.user_agents:
            return

        request.headers['user-agent'] = choice(self.user_agents)
        #logging.log(logging.INFO, "RotateUserAgentMiddleware::process_request(*****): user-agent=%s" % (request.headers['user-agent']))
        print("RotateUserAgentMiddleware::process_request(*****): user-agent=%s" % (request.headers['user-agent']))


class CheckIfAlreadyAvailableMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        spider.logger.info('CheckIfAlreadyAvailableMiddleware:process_spider_input() Spider: %s, Response: %s' % spider.name, response)
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        spider.logger.info('CheckIfAlreadyAvailableMiddleware:process_spider_output() Spider: %s' % spider.name)
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        spider.logger.info('CheckIfAlreadyAvailableMiddleware:process_spider_exception() Spider: %s' % spider.name)
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        spider.logger.info('CheckIfAlreadyAvailableMiddleware:process_start_requests() Spider: %s' % spider.name)
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('CheckIfAlreadyAvailableMiddleware: Spider opened: %s' % spider.name)

        
# class RandomUserAgentMiddleware(object):
    # def __init__(self, crawler):
        # super(RandomUserAgentMiddleware, self).__init__()

        # fallback = crawler.settings.get('FAKEUSERAGENT_FALLBACK', None)
        # self.ua = UserAgent(fallback=fallback)
        # self.per_proxy = crawler.settings.get('RANDOM_UA_PER_PROXY', False)
        # self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')
        # self.proxy2ua = {}

    # @classmethod
    # def from_crawler(cls, crawler):
        # return cls(crawler)

    # def process_request(self, request, spider):
        # def get_ua():
            # '''Gets random UA based on the type setting (random, firefox…)'''
            # return getattr(self.ua, self.ua_type)
        
        # if self.per_proxy:
            # proxy = request.meta.get('proxy')
            # if proxy not in self.proxy2ua:
                # self.proxy2ua[proxy] = get_ua()
                # logger.debug('Assign User-Agent %s to Proxy %s'
                             # % (self.proxy2ua[proxy], proxy))
            # request.headers.setdefault('User-Agent', self.proxy2ua[proxy])
        # else:
            # request.headers.setdefault('User-Agent', get_ua())
            
