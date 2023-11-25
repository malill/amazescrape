# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AmazonScrapingInfo:
    """Contains information about the scraping process."""

    search_term: str | None = field(default=None)
    domain: str | None = field(default=None)
    s_url: str | None = field(default=None)
    s_timestamp: datetime | None = field(default=None)


@dataclass
class AmazonItem:
    '''Contains information about a single product.'''

    # PRODUCT SEARCH PAGE (PSP) INFORMATION
    # Scraping information
    search_term: str | None = field(default=None)
    domain: str | None = field(default=None)
    s_url: str | None = field(default=None)
    s_timestamp: datetime | None = field(default=None)

    # Basic info about the product
    s_asin: str | None = field(default=None)
    s_name: str | None = field(default=None)

    # Image
    image_urls: list[str] | None = field(default=None)  # Needed for scrapy ImagesPipeline
    images: None = field(default=None)  # Needed for scrapy ImagesPipeline
    s_image_filename: str | None = field(default=None)

    # List or grid
    s_display: str | None = field(default=None)

    # Rating
    s_rating_avg: str | None = field(default=None)
    s_rating_n: str | None = field(default=None)

    # Price
    s_price: str | None = field(default=None)
    s_price_strike: str | None = field(default=None)

    # Page ranking
    s_rank: str | None = field(default=None)

    # Delivery info
    s_delivery: str | None = field(default=None)

    # Left in stock
    s_left_in_stock: str | None = field(default=None)

    # Other offers
    s_other_price_min: str | None = field(default=None)
    s_other_n: str | None = field(default=None)

    # Badges
    sb_status_prop: str | None = field(default=None)
    sb_status_text: str | None = field(default=None)
    sb_sponsored: str | None = field(default=None)
    sb_bought_last_month: str | None = field(default=None)
    sb_lightning_deal: str | None = field(default=None)
    sb_promotion: str | None = field(default=None)
    sb_prime: str | None = field(default=None)
    sb_coupon: str | None = field(default=None)

    # Other bagdes
    sb_other_01: str | None = field(default=None)
    sb_other_02: str | None = field(default=None)
    sb_other_03: str | None = field(default=None)

    # PRODUCT DETAIL PAGE (PDP) INFORMATION
    # Basic information
    p_url: str | None = field(default=None)
    p_timestamp: datetime | None = field(default=None)

    # Buy box
    p_fulfiller_name: str | None = field(default=None)  # "Versand", "Dispatches from"
    p_merchant_id: str | None = field(default=None)  # aka seller_id
    p_merchant_name: str | None = field(default=None)  # "Verkäufer", "Sold by"

    # Best seller rank
    p_bestseller_rank: str | None = field(default=None)

    # Rating distribution
    p_rating_1_star: str | None = field(default=None)
    p_rating_2_star: str | None = field(default=None)
    p_rating_3_star: str | None = field(default=None)
    p_rating_4_star: str | None = field(default=None)
    p_rating_5_star: str | None = field(default=None)

    # Reviews
    p_review_1_rating: str | None = field(default=None)
    p_review_1_title: str | None = field(default=None)
    p_review_1_text: str | None = field(default=None)
    p_review_2_rating: str | None = field(default=None)
    p_review_2_title: str | None = field(default=None)
    p_review_2_text: str | None = field(default=None)
    p_review_3_rating: str | None = field(default=None)
    p_review_3_title: str | None = field(default=None)
    p_review_3_text: str | None = field(default=None)
