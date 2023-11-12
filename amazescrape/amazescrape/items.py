# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass, field

@dataclass
class AmazonItem:
    # Basic info about the product
    asin: str | None = field(default=None)
    name: str | None = field(default=None)
    current_timestamp: str | None = field(default=None)

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
