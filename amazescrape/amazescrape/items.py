# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AmazonItem:
    # Scraping info
    prefix: str | None = field(default=None)
    suffix: str | None = field(default=None)
    url: str | None = field(default=None)
    request_timestamp: datetime | None = field(default=None)

    # Basic info about the product
    asin: str | None = field(default=None)
    name: str | None = field(default=None)

    # Rating
    rating_avg: str | None = field(default=None)
    rating_n: str | None = field(default=None)

    # Price
    price: str | None = field(default=None)
    price_strike: str | None = field(default=None)

    # Page ranking
    rank: str | None = field(default=None)

    # Badges
    status_badge: str | None = field(default=None)
    prime: str | None = field(default=None)

@dataclass
class AmazonScrapingInfo:
    prefix: str | None = field(default=None)
    suffix: str | None = field(default=None)
    url: str | None = field(default=None)
    request_timestamp: datetime | None = field(default=None)
