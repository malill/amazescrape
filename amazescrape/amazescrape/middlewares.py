from random import choice

class RandomUserAgentMiddleware:
    """Middleware to randomly select a user agent for each request."""

    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your middleware instance and pass the settings object
        return cls(crawler.settings.getlist('USER_AGENT_LIST'))

    def process_request(self, request, spider):
        '''Assign a random user agent.'''
        if self.user_agents:
            request.headers.setdefault('User-Agent', choice(self.user_agents))
