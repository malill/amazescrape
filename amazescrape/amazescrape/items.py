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

    # Badges
    top_badge: str | None = field(default=None)
    prime: str | None = field(default=None)
