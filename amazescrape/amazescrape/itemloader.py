from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class AmazonItemLoader(ItemLoader):
    '''Item loader for AmazonItem.

    Args:
        ItemLoader (_type_): The item loader to use.
    '''

    default_output_processor = TakeFirst()
