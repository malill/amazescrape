from amazescrape.spiders.AmazonSpider import AmazonSpider
from amazescrape.items import AmazonItem


class AmazescrapePipeline:
    def process_item(self, amazon_item: AmazonItem, spider: AmazonSpider) -> AmazonItem:
        return amazon_item
