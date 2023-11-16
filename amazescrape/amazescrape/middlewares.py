# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


class RandomUserAgentMiddleware:
    """This middleware allows spiders to override the user_agent"""

    def __init__(self, user_agent="Scrapy"):
        self.user_agent = self.get_random_user_agent()

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.settings["USER_AGENT"])
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def spider_opened(self, spider):
        self.user_agent = getattr(spider, "user_agent", self.user_agent)

    def process_request(self, request, spider):
        '''Override the request's user agent.'''
        self.user_agent = self.get_random_user_agent()
        if self.user_agent:
            request.headers.setdefault(b"User-Agent", self.user_agent)

    def get_random_user_agent(self) -> str:
        '''Get a random user agent string.'''
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
        return user_agent_rotator.get_random_user_agent()
