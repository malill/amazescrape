# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AmazonScrapingInfo:
    """Contains information about the scraping process."""

    prefix: str | None = field(default=None)
    suffix: str | None = field(default=None)
    url: str | None = field(default=None)
    request_timestamp: datetime | None = field(default=None)


@dataclass
class AmazonItem:
    """Contains information about a single product."""

    # PRODUCT SEARCH PAGE (PSP) INFORMATION
    # Scraping information
    prefix: str | None = field(default=None)
    suffix: str | None = field(default=None)
    url: str | None = field(default=None)
    request_timestamp: datetime | None = field(default=None)

    # Basic info about the product
    asin: str | None = field(default=None)
    name: str | None = field(default=None)

    # Image
    image_urls: list[str] | None = field(default=None)
    images: None = field(default=None)
    image_filename: str | None = field(default=None)

    # Rating
    s_rating_avg: str | None = field(default=None)
    s_rating_n: str | None = field(default=None)

    # Price
    s_price: str | None = field(default=None)
    s_price_strike: str | None = field(default=None)

    # Page ranking
    s_rank: str | None = field(default=None)

    # Badges
    sb_status_prop: str | None = field(default=None)
    sb_status_text: str | None = field(default=None)
    sb_prime: str | None = field(default=None)

    # PRODUCT DETAIL PAGE (PDP) INFORMATION
    # Basic information
    p_url: str | None = field(default=None)

    # Buy box
    p_fulfiller_id: str | None = field(default=None)  # TODO: check if available
    p_fulfiller_name: str | None = field(default=None)  # "Versand", "Dispatches from"
    p_merchant_id: str | None = field(default=None)  # aka seller_id
    p_merchant_name: str | None = field(default=None)  # "Verkäufer", "Sold by"
