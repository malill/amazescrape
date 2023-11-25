from random import choice


class RandomUserAgentMiddleware:
    '''Middleware to randomly select a user agent for each request.'''

    def __init__(self, user_agents):
        '''Initializes the middleware.

        Args:
            user_agents (_type_): The list of user agents to use.
        '''
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        '''Initializes the middleware from the crawler. Used by Scrapy to create your middleware instance and pass the
        settings object

        Args:
            crawler (_type_): The crawler to use.

        Returns:
            _type_: The middleware instance.
        '''
        return cls(crawler.settings.getlist('USER_AGENT_LIST'))

    def process_request(self, request, spider):
        '''Processes the request and sets the user agent header.

        Args:
            request (_type_): _description_
            spider (_type_): _description_
        '''
        if self.user_agents:
            request.headers.setdefault('User-Agent', choice(self.user_agents))
