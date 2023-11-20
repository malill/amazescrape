import json
from pathlib import PurePosixPath
from urllib.parse import urlparse

from lxml.html import document_fromstring

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
            amazon_item.s_price = self.get_digits(amazon_item.s_price)
        if amazon_item.s_price_strike is not None:
            amazon_item.s_price_strike = self.get_digits(amazon_item.s_price_strike)

        # Transform left in stock
        if amazon_item.s_left_in_stock is not None:
            amazon_item.s_left_in_stock = self.get_digits(amazon_item.s_left_in_stock)

        # Transform the other offers
        if amazon_item.s_other_price_min is not None:
            amazon_item.s_other_price_min = self.get_digits(amazon_item.s_other_price_min)
        if amazon_item.s_other_n is not None:
            amazon_item.s_other_n = self.get_digits(amazon_item.s_other_n)

        # Transform the badge type
        if amazon_item.sb_status_prop is not None:
            amazon_item.sb_status_prop = json.loads(amazon_item.sb_status_prop)["badgeType"]

        # Transform the best seller rank
        if amazon_item.p_bestseller_rank is not None:
            bsr_str = amazon_item.p_bestseller_rank
            doc = document_fromstring(bsr_str)
            amazon_item.p_bestseller_rank = doc.text_content().strip()

        return amazon_item

    def get_digits(self, text_content: str) -> str:
        return ''.join(filter(lambda x: x.isdigit(), text_content))


# pipelines.py

import sqlite3


class SQLitePipeline:
    def __init__(self):
        self.con = sqlite3.connect('../res/amazescrape.db')
        self.cur = self.con.cursor()

        # Create table with fields corresponding to AmazonItem
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS amazon_items(
                prefix TEXT,
                suffix TEXT,
                url TEXT,
                request_timestamp TEXT,
                asin TEXT,
                name TEXT,
                image_filename TEXT,
                s_display TEXT,
                s_rating_avg INTEGER,
                s_rating_n INTEGER,
                s_price INTEGER,
                s_price_strike INTEGER,
                s_rank INTEGER,
                s_delivery TEXT,
                s_left_in_stock INTEGER,
                s_other_price_min INTEGER,
                s_other_n INTEGER,
                sb_status_prop TEXT,
                sb_status_text TEXT,
                sb_sponsored TEXT,
                sb_lightning_deal TEXT,
                sb_promotion TEXT,
                sb_prime TEXT,
                sb_coupon TEXT,
                p_url TEXT,
                p_fulfiller_id TEXT,
                p_fulfiller_name TEXT,
                p_merchant_id TEXT,
                p_merchant_name TEXT,
                p_bestseller_rank TEXT
            )
            """
        )

    def process_item(self, item, spider):
        # Serialize list and datetime fields
        image_urls = ','.join(item.image_urls) if item.image_urls else None
        request_timestamp = item.request_timestamp.isoformat() if item.request_timestamp else None

        self.cur.execute(
            """
            INSERT INTO amazon_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.prefix,
                item.suffix,
                item.url,
                request_timestamp,
                item.asin,
                item.name,
                item.image_filename,
                item.s_display,
                item.s_rating_avg,
                item.s_rating_n,
                item.s_price,
                item.s_price_strike,
                item.s_rank,
                item.s_delivery,
                item.s_left_in_stock,
                item.s_other_price_min,
                item.s_other_n,
                item.sb_status_prop,
                item.sb_status_text,
                item.sb_sponsored,
                item.sb_lightning_deal,
                item.sb_promotion,
                item.sb_prime,
                item.sb_coupon,
                item.p_url,
                item.p_fulfiller_id,
                item.p_fulfiller_name,
                item.p_merchant_id,
                item.p_merchant_name,
                item.p_bestseller_rank,
            ),
        )

        self.con.commit()
        return item

    def close_spider(self, spider):
        self.con.close()
