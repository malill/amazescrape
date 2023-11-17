import json
from pathlib import PurePosixPath
from urllib.parse import urlparse

from scrapy.pipelines.images import ImagesPipeline
from amazescrape.spiders.AmazonSpider import AmazonSpider
from amazescrape.items import AmazonItem

# TODO: store the scraped data in a database
# TODO: store product images in file system (https://docs.scrapy.org/en/latest/topics/media-pipeline.html?highlight=image)


class AmazonImagePipeline(ImagesPipeline):
    '''Pipeline for downloading images from Amazon.'''

    def file_path(self, request, response=None, info=None, *, item: AmazonItem = None):
        '''Returns the file path for storing the image. The image is stored in the `images` directory. The file name is
        the same as the original file name, that is extracted from the image URL.'''
        original_file_name = PurePosixPath(urlparse(request.url).path).name
        item.image_filename = original_file_name
        return original_file_name


class AmazonItemPipeline:
    '''Pipeline for processing scraped values.'''

    def process_item(self, amazon_item: AmazonItem, spider: AmazonSpider) -> AmazonItem:
        # Transform the rating
        if amazon_item.s_rating_avg is not None:
            amazon_item.s_rating_avg = ''.join(filter(lambda x: x.isdigit(), amazon_item.s_rating_avg[:3]))
        if amazon_item.s_rating_n is not None:
            amazon_item.s_rating_n = ''.join(filter(lambda x: x.isdigit(), amazon_item.s_rating_n))

        # Transform the price
        if amazon_item.s_price is not None:
            amazon_item.s_price = self.fix_price(amazon_item.s_price)
        if amazon_item.s_price_strike is not None:
            amazon_item.s_price_strike = self.fix_price(amazon_item.s_price_strike)

        # Transform the badge type
        if amazon_item.sb_status_prop is not None:
            amazon_item.sb_status_prop = json.loads(amazon_item.sb_status_prop)["badgeType"]

        return amazon_item

    def fix_price(self, price_str: str) -> str:
        return ''.join(filter(lambda x: x.isdigit(), price_str))


class AmazonItemDBStoragePipeline:
    '''Pipeline for storing scraped data in a SQLite database.'''

    def process_item(self, amazon_item: AmazonItem, spider: AmazonSpider) -> AmazonItem:
        # Store item in database
        return amazon_item
