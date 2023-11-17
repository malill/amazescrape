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
    rating_avg: int | None = field(default=None)
    rating_n: int | None = field(default=None)

    # Price
    price: int | None = field(default=None)
    price_strike: int | None = field(default=None)

    # Page ranking
    rank: int | None = field(default=None)

    # Badges
    status_badge_prop: str | None = field(default=None)
    status_badge_text: str | None = field(default=None)
    prime: str | None = field(default=None)

    # PRODUCT DETAIL PAGE (PDP) INFORMATION
    # Basic information
    pdp_url: str | None = field(default=None)
    pdp_title: str | None = field(default=None)

    # Buy box
    fulfiller_id: str | None = field(default=None)  # TODO: check if available
    fulfiller_name: str | None = field(default=None)  # "Versand", "Dispatches from"
    merchant_id: str | None = field(default=None)  # aka seller_id
    merchant_name: str | None = field(default=None)  # "Verkäufer", "Sold by"
