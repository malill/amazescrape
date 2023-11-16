import json
from pathlib import PurePosixPath
from urllib.parse import urlparse

from scrapy.pipelines.images import ImagesPipeline
from amazescrape.spiders.AmazonSpider import AmazonSpider
from amazescrape.items import AmazonItem

# TODO: store the scraped data in a database
# TODO: store product images in file system (https://docs.scrapy.org/en/latest/topics/media-pipeline.html?highlight=image)


class AmazonItemPipeline:
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
        if amazon_item.status_badge_prop is not None:
            amazon_item.status_badge_prop = json.loads(amazon_item.status_badge_prop)["badgeType"]

        return amazon_item

    def fix_price(self, price_str: str) -> str:
        return ''.join(filter(lambda x: x.isdigit(), price_str))


class AmazonImagePipeline(ImagesPipeline):
    '''Pipeline for downloading images from Amazon.'''

    def file_path(self, request, response=None, info=None, *, item: AmazonItem = None):
        '''Returns the file path for storing the image. The path is relative to the project root. The image is stored in
        the `files` directory. The file name is the same as the original file name. The original file name is extracted
        from the URL. The URL is the image URL from the scraped data.'''
        original_file_name = PurePosixPath(urlparse(request.url).path).name
        item.image_filename = original_file_name
        return "files/" + original_file_name
