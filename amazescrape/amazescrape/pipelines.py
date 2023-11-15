import json
from amazescrape.spiders.AmazonSpider import AmazonSpider
from amazescrape.items import AmazonItem


class AmazescrapePipeline:
    def process_item(self, amazon_item: AmazonItem, spider: AmazonSpider) -> AmazonItem:
        # Transform the rating
        if amazon_item.rating_avg is not None:
            amazon_item.rating_avg = ''.join(filter(lambda x: x.isdigit(), amazon_item.rating_avg[:3]))
        if amazon_item.rating_n is not None:
            amazon_item.rating_n = ''.join(filter(lambda x: x.isdigit(), amazon_item.rating_n))

        # Transform the price
        if amazon_item.price is not None:
            amazon_item.price = self.fix_price(amazon_item.price)
        if amazon_item.price_strike is not None:
            amazon_item.price_strike = self.fix_price(amazon_item.price_strike)

        # Transform the badge type
        if amazon_item.status_badge is not None:
            amazon_item.status_badge = json.loads(amazon_item.status_badge)["badgeType"]

        return amazon_item

    def fix_price(self, price_str: str) -> str:
        return ''.join(filter(lambda x: x.isdigit(), price_str))
