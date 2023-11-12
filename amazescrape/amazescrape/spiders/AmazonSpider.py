from datetime import datetime
import scrapy
from scrapy import Request
from scrapy.http import Response
from amazescrape.itemloader import AmazonItemLoader

from amazescrape.items import AmazonItem


class AmazonSpider(scrapy.Spider):
    name = "amazon"

    def start_requests(self) -> Request:
        urls = ["https://www.amazon.de/s?k=laptop"]
        for url in urls:
            current_time = datetime.now()
            formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            self.request_timestamp = formatted_time
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response: Response) -> AmazonItem:
        search_results = response.xpath(
            "//div[@data-asin and @data-index and @data-uuid and @data-component-type='s-search-result']"
        )
        self.logger.info(f"Found {len(search_results)} search results on {response.url}")

        for search_result in search_results:
            yield self.load_amazon_item(search_result)

    def load_amazon_item(self, response: Response) -> AmazonItem:
        item_loader = AmazonItemLoader(item=AmazonItem(), selector=response)

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

        item_loader.add_value("current_timestamp", self.request_timestamp)

        return item_loader.load_item()
