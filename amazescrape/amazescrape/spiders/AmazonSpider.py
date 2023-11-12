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
        item_loader.add_xpath("asin", "./@data-asin")
        item_loader.add_xpath("name", ".//h2//text()")

        # Badges
        ## Top Badge
        item_loader.add_xpath("top_badge", ".//span[contains(@class, 'badge-text')]/text()")

        ## Amazon Prime
        item_loader.add_xpath("prime", ".//i[contains(@class, 'a-icon-prime')]/@aria-label")
        return item_loader.load_item()
