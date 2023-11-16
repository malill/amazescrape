from datetime import datetime
import scrapy
from scrapy import Request
from scrapy.http import Response
from amazescrape.itemloader import AmazonItemLoader
from amazescrape.items import AmazonItem, AmazonScrapingInfo
import csv


class AmazonSpider(scrapy.Spider):
    name = "amazon"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scraping_infos = self.read_scraping_infos()

    def read_scraping_infos(self):
        filepath = "../res/mock_urls.csv"
        try:
            with open(filepath, "r") as f:
                csv_reader = csv.reader(f, delimiter=';')
                next(csv_reader)  # Skip the header line
                return [AmazonScrapingInfo(*row) for row in csv_reader if row]
        except IOError as e:
            self.logger.error(f"Error reading file: {e}")
            return []

    def start_requests(self) -> Request:
        for scraping_info in self.scraping_infos:
            scraping_info.request_timestamp = datetime.now()
            yield scrapy.Request(url=scraping_info.url, callback=self.parse, meta={"scraping_info": scraping_info})

    def parse(self, response: Response) -> AmazonItem:
        search_results = response.xpath(
            "//div[@data-asin and @data-index and @data-uuid and @data-component-type='s-search-result']"
        )

        if not search_results:
            self.logger.warning(f"No search results found on {response.url}")
            return

        self.logger.info(f"Found {len(search_results)} search results on {response.url}")
        scraping_info = response.meta.get('scraping_info')

        for search_result in search_results:
            amazon_item = self.load_amazon_search_item(search_result, scraping_info)
            product_url = search_result.xpath(".//h2//a[contains(@class, 'a-link-normal')]/@href")
            # product_url = self.create_url(amazon_item)
            if product_url:
                url = product_url[0].get()
                if url is not None:
                    # follow
                    amazon_item.pdp_url = url
                    yield response.follow(
                        url,
                        callback=self.parse_product_page,
                        meta={"amazon_item": amazon_item, "fallback_item": amazon_item, "handle_httpstatus_all": True},
                        errback=self.handle_request_failure,
                    )

                    # yield scrapy.Request(
                    #     url=product_url,
                    #     callback=self.parse_product_page,
                    #     meta={"amazon_item": amazon_item, "fallback_item": amazon_item, "handle_httpstatus_all": True},
                    #     errback=self.handle_request_failure,
                    # )
            else:
                yield amazon_item

    def create_url(self, amazon_item: AmazonItem) -> str:
        if amazon_item and amazon_item.asin:
            return f"https://www.amazon.de/dp/{amazon_item.asin}"
        self.logger.error("Missing ASIN in Amazon item.")
        return None

    def handle_request_failure(self, failure):
        self.logger.error(f"Request failed: {failure.request.url}")
        # Yield the fallback item
        yield failure.request.meta.get('fallback_item')

    def parse_product_page(self, response: Response) -> AmazonItem:
        amazon_item = response.meta.get("amazon_item")
        if amazon_item:
            amazon_item = self.load_amazon_product_page(amazon_item, response)
            yield amazon_item
        else:
            self.logger.error("Amazon item not found in response meta.")

    def load_amazon_product_page(self, amazon_item: AmazonItem, response: Response) -> AmazonItem:
        item_loader = AmazonItemLoader(item=amazon_item, selector=response)
        item_loader.add_value("pdp_url", response.url)
        item_loader.add_xpath("merchant_id", "//*[@id='merchantID']/@value")
        item_loader.add_xpath("pdp_title", "//span[@id='productTitle']//text()")

        buy_box_element = response.xpath("//div[@id='offer-display-features']")

        if buy_box_element:
            item_loader.add_xpath(
                "fulfiller",
                "//div[@id='offer-display-features']//div[@offer-display-feature-name='desktop-fulfiller-info'][2]//span//text()",
            )

        return item_loader.load_item()

    def load_amazon_search_item(self, response: Response, scraping_info: AmazonScrapingInfo) -> AmazonItem:
        item_loader = AmazonItemLoader(item=AmazonItem(), selector=response)

        # Scraping info
        if scraping_info:
            item_loader.add_value("prefix", scraping_info.prefix)
            item_loader.add_value("suffix", scraping_info.suffix)
            item_loader.add_value("url", scraping_info.url)
            item_loader.add_value("request_timestamp", scraping_info.request_timestamp)

        # Basic information
        item_loader.add_xpath("asin", "./@data-asin")
        item_loader.add_xpath("name", ".//h2//text()")

        # Ratings
        item_loader.add_xpath("rating_avg", ".//span[@class='a-icon-alt']/text()")
        item_loader.add_xpath("rating_n", ".//span[@class='a-size-base s-underline-text']/text()")

        # Price
        item_loader.add_xpath("price", ".//span[@class='a-price']/span[@class='a-offscreen']/text()")
        item_loader.add_xpath("price_strike", ".//span[@data-a-strike='true']/span/text()")

        # Page ranking
        item_loader.add_xpath("rank", "./@data-index")

        # Badges
        ## Top Badge
        item_loader.add_xpath(
            "status_badge", ".//span[@data-component-type='s-status-badge-component']//@data-component-props"
        )

        ## Amazon Prime
        item_loader.add_xpath("prime", ".//i[contains(@class, 'a-icon-prime')]/@aria-label")

        return item_loader.load_item()
