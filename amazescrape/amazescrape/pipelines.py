import json
import logging
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from lxml.html import document_fromstring
from scrapy.exceptions import DropItem

from scrapy.pipelines.images import ImagesPipeline
from amazescrape.spiders.AmazonSpider import AmazonSpider
from amazescrape.items import AmazonItem


class AmazonImagePipeline(ImagesPipeline):
    '''Pipeline for downloading images from Amazon.'''

    def file_path(self, request, response=None, info=None, *, item: AmazonItem = None):
        '''Returns the file path for storing the image. The image is stored in the `images` directory. The file name is
        the same as the original file name, that is extracted from the image URL.'''
        original_file_name = Path(urlparse(request.url).path).name
        item.s_image_filename = original_file_name
        return f'{original_file_name}'


class AmazonItemPipeline:
    '''Pipeline for processing scraped values.'''

    def process_item(self, amazon_item: AmazonItem, spider: AmazonSpider) -> AmazonItem:
        '''Processes scraped values.

        Args:
            amazon_item (AmazonItem): The scraped item to process.
            spider (AmazonSpider): The spider that scraped the item.

        Raises:
            DropItem: If there is an error processing the item.
            DropItem: If the item does not have an ASIN.

        Returns:
            AmazonItem: The processed item.
        '''
        try:
            # List of fields to process with get_digits function
            digit_fields = [
                's_rating_avg',
                's_rating_n',
                's_price',
                's_price_strike',
                's_left_in_stock',
                's_other_price_min',
                's_other_n',
                'sb_bought_last_month',
                'p_review_1_rating',
                'p_review_2_rating',
                'p_review_3_rating',
            ]

            # Process fields that require digit extraction
            for field in digit_fields:
                if getattr(amazon_item, field) is not None:
                    setattr(amazon_item, field, self.get_digits(getattr(amazon_item, field)))

            # Special handling for badge type
            if amazon_item.sb_status_prop is not None:
                amazon_item.sb_status_prop = json.loads(amazon_item.sb_status_prop)["badgeType"]

            # Special handling for best seller rank
            if amazon_item.p_bestseller_rank is not None:
                bsr_str = amazon_item.p_bestseller_rank
                doc = document_fromstring(bsr_str)
                amazon_item.p_bestseller_rank = doc.text_content().strip()

            # Ensure ASIN is present
            if not amazon_item.s_asin:
                raise DropItem("Missing ASIN in item")

        except Exception as e:
            logging.error(f"Error processing item: {e}")
            raise DropItem(f"Error processing item: {e}")

        return amazon_item

    def get_digits(self, text_content: str) -> str:
        '''Extracts digits from a string.

        Args:
            text_content (str): The string to extract digits from.

        Returns:
            str: The extracted digits.
        '''
        return ''.join(filter(lambda x: x.isdigit(), text_content))


class SQLitePipeline:
    def __init__(self) -> None:
        '''Initializes the SQLite pipeline.'''
        self.con = sqlite3.connect('../res/amazescrape.db')
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self) -> None:
        '''Creates the database table if it does not exist.'''
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS amazon_items(
                search_term TEXT,
                domain TEXT,
                s_url TEXT,
                s_timestamp TEXT,
                s_asin TEXT,
                s_name TEXT,
                s_image_filename TEXT,
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
                sb_bought_last_month TEXT,
                sb_lightning_deal TEXT,
                sb_promotion TEXT,
                sb_prime TEXT,
                sb_coupon TEXT,
                sb_other_01 TEXT,
                sb_other_02 TEXT,
                sb_other_03 TEXT,
                p_url TEXT,
                p_timestamp TEXT,
                p_fulfiller_name TEXT,
                p_merchant_id TEXT,
                p_merchant_name TEXT,
                p_bestseller_rank TEXT,
                p_rating_1_star TEXT,
                p_rating_2_star TEXT,
                p_rating_3_star TEXT,
                p_rating_4_star TEXT,
                p_rating_5_star TEXT,
                p_review_1_rating TEXT,
                p_review_1_title TEXT,
                p_review_1_text TEXT,
                p_review_2_rating TEXT,
                p_review_2_title TEXT,
                p_review_2_text TEXT,
                p_review_3_rating TEXT,
                p_review_3_title TEXT,
                p_review_3_text TEXT
            )
            """
        )

    def process_item(self, amazon_item: AmazonItem, spider: AmazonSpider) -> AmazonItem:
        '''Inserts scraped item into database.

        Args:
            amazon_item (AmazonItem): The scraped item to insert into the database.
            spider (AmazonSpider): The spider that scraped the item.

        Raises:
            DropItem: If there is an error inserting the item into the database.

        Returns:
            AmazonItem: The persisted item.
        '''
        try:
            # Serialize list and datetime fields
            s_timestamp = amazon_item.s_timestamp.isoformat() if amazon_item.s_timestamp else None
            p_timestamp = amazon_item.p_timestamp.isoformat() if amazon_item.p_timestamp else None

            # Prepare data for insertion
            item_data = {
                'search_term': amazon_item.search_term,
                'domain': amazon_item.domain,
                's_url': amazon_item.s_url,
                's_timestamp': s_timestamp,
                's_asin': amazon_item.s_asin,
                's_name': amazon_item.s_name,
                's_image_filename': amazon_item.s_image_filename,
                's_display': amazon_item.s_display,
                's_rating_avg': amazon_item.s_rating_avg,
                's_rating_n': amazon_item.s_rating_n,
                's_price': amazon_item.s_price,
                's_price_strike': amazon_item.s_price_strike,
                's_rank': amazon_item.s_rank,
                's_delivery': amazon_item.s_delivery,
                's_left_in_stock': amazon_item.s_left_in_stock,
                's_other_price_min': amazon_item.s_other_price_min,
                's_other_n': amazon_item.s_other_n,
                'sb_status_prop': amazon_item.sb_status_prop,
                'sb_status_text': amazon_item.sb_status_text,
                'sb_sponsored': amazon_item.sb_sponsored,
                'sb_bought_last_month': amazon_item.sb_bought_last_month,
                'sb_lightning_deal': amazon_item.sb_lightning_deal,
                'sb_promotion': amazon_item.sb_promotion,
                'sb_prime': amazon_item.sb_prime,
                'sb_coupon': amazon_item.sb_coupon,
                'sb_other_01': amazon_item.sb_other_01,
                'sb_other_02': amazon_item.sb_other_02,
                'sb_other_03': amazon_item.sb_other_03,
                'p_url': amazon_item.p_url,
                'p_timestamp': p_timestamp,
                'p_fulfiller_name': amazon_item.p_fulfiller_name,
                'p_merchant_id': amazon_item.p_merchant_id,
                'p_merchant_name': amazon_item.p_merchant_name,
                'p_bestseller_rank': amazon_item.p_bestseller_rank,
                'p_rating_1_star': amazon_item.p_rating_1_star,
                'p_rating_2_star': amazon_item.p_rating_2_star,
                'p_rating_3_star': amazon_item.p_rating_3_star,
                'p_rating_4_star': amazon_item.p_rating_4_star,
                'p_rating_5_star': amazon_item.p_rating_5_star,
                'p_review_1_rating': amazon_item.p_review_1_rating,
                'p_review_1_title': amazon_item.p_review_1_title,
                'p_review_1_text': amazon_item.p_review_1_text,
                'p_review_2_rating': amazon_item.p_review_2_rating,
                'p_review_2_title': amazon_item.p_review_2_title,
                'p_review_2_text': amazon_item.p_review_2_text,
                'p_review_3_rating': amazon_item.p_review_3_rating,
                'p_review_3_title': amazon_item.p_review_3_title,
                'p_review_3_text': amazon_item.p_review_3_text,
            }

            # Construct query with parameter substitution
            fields = ', '.join(item_data.keys())
            placeholders = ', '.join('?' * len(item_data))
            query = f"INSERT INTO amazon_items ({fields}) VALUES ({placeholders})"

            # Execute the query
            self.cur.execute(query, tuple(item_data.values()))
            self.con.commit()

        except sqlite3.DatabaseError as e:
            logging.error(f"Error inserting item into database: {e}")
            raise DropItem(f"Error inserting item into database: {e}")

        return amazon_item

    def close_spider(self, spider: AmazonSpider) -> None:
        '''Closes the database connection.

        Args:
            spider (AmazonSpider): The spider that scraped the item.
        '''
        self.con.close()
