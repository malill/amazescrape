from datetime import datetime
import scrapy
from scrapy import Request
from scrapy.http import Response
from amazescrape.itemloader import AmazonItemLoader

from amazescrape.items import AmazonItem, AmazonScrapingInfo


class AmazonSpider(scrapy.Spider):
    name = "amazon"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scraping_infos = self.read_scraping_infos()

    def read_scraping_infos(self):
        filepath = "../res/mock_urls.csv"
        try:
            with open(filepath, "r") as f:
                next(f)  # Skip the header line
                return [AmazonScrapingInfo(*line.strip().split(";")) for line in f if line.strip()]
        except IOError as e:
            self.logger.error(f"Error reading file: {e}")
            return []

    def start_requests(self) -> Request:
        for scraping_info in self.scraping_infos:
            scraping_info.request_timestamp = datetime.now()
            yield scrapy.Request(url=scraping_info.url, callback=self.parse, meta={"scraping_info": scraping_info})

    def parse(self, response: Response) -> AmazonItem:
        search_results = response.xpath(
            "//div[@data-asin and @data-index and @data-uuid and @data-component-type='s-search-result']"
        )
        self.logger.info(f"Found {len(search_results)} search results on {response.url}")
        scraping_info = response.meta.get('scraping_info')

        for search_result in search_results:
            yield self.load_amazon_item(search_result, scraping_info)

    def load_amazon_item(self, response: Response, scraping_info: AmazonScrapingInfo) -> AmazonItem:
        item_loader = AmazonItemLoader(item=AmazonItem(), selector=response)

        # Scraping info
        if scraping_info:
            item_loader.add_value("prefix", scraping_info.prefix)
            item_loader.add_value("suffix", scraping_info.suffix)
            item_loader.add_value("url", scraping_info.url)
            item_loader.add_value("request_timestamp", scraping_info.request_timestamp)

        # Basic information
        item_loader.add_xpath("asin", "./@data-asin")
        item_loader.add_xpath("name", ".//h2//text()")

        # Ratings
        item_loader.add_xpath("rating_avg", ".//span[@class='a-icon-alt']/text()")
        item_loader.add_xpath("rating_n", ".//span[@class='a-size-base s-underline-text']/text()")

        # Price
        item_loader.add_xpath("price", ".//span[@class='a-price']/span[@class='a-offscreen']/text()")
        item_loader.add_xpath("price_strike", ".//span[@data-a-strike='true']/span/text()")

        # Page ranking
        item_loader.add_xpath("rank", "./@data-index")

        # Badges
        ## Top Badge
        item_loader.add_xpath(
            "status_badge", ".//span[@data-component-type='s-status-badge-component']//@data-component-props"
        )

        ## Amazon Prime
        item_loader.add_xpath("prime", ".//i[contains(@class, 'a-icon-prime')]/@aria-label")

        return item_loader.load_item()
