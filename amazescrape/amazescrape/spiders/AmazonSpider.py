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

    @staticmethod
    def get_search_item_field_mappings() -> dict[str, str]:
        return {
            "asin": "./@data-asin",
            "name": ".//h2//text()",
            "image_urls": ".//img[@class='s-image']/@src",
            "s_rating_avg": ".//span[@class='a-icon-alt']/text()",
            "s_rating_n": ".//span[@class='a-size-base s-underline-text']/text()",
            "s_price": ".//span[@class='a-price']/span[@class='a-offscreen']/text()",
            "s_price_strike": ".//span[@data-a-strike='true']/span/text()",
            "s_rank": "./@data-index",
            "s_delivery": ".//div[@class='a-row a-size-base a-color-secondary s-align-children-center']//@aria-label",
            "s_left_in_stock": ".//span[@class='a-size-base a-color-price']",
            "s_other_price_min": ".//div[@class='a-section a-spacing-none a-spacing-top-mini']//div[@class='a-row a-size-base a-color-secondary']//span[@class='a-color-base']//text()",
            "s_other_n": ".//div[@class='a-section a-spacing-none a-spacing-top-mini']//div[@class='a-row a-size-base a-color-secondary']//span[@class='a-declarative']//a//text()",
            "sb_status_prop": ".//span[@data-component-type='s-status-badge-component']//@data-component-props",
            "sb_status_text": ".//span[@data-component-type='s-status-badge-component']//@data-csa-c-badge-text",
            "sb_sponsored": ".//a[contains(@class, 'puis-sponsored-label-text')]//span[@class='a-color-secondary']/text()",
            "sb_lightning_deal": ".//span[@data-a-badge-color='sx-lightning-deal-red']//span[@class='a-badge-text']//text()",
            "sb_promotion": ".//span[@class='a-size-base s-highlighted-text-padding aok-inline-block s-promotion-highlight-color']/text()",
            "sb_prime": ".//i[contains(@class, 'a-icon-prime')]/@aria-label",
            "sb_coupon": ".//span[@class='s-coupon-unclipped']//span[contains(@class, 's-coupon-highlight-color')]/text()",
        }

    @staticmethod
    def get_product_page_field_mappings() -> list[tuple[str, str]]:
        return [
            ("p_merchant_id", "//*[@id='merchantID']/@value"),
            (
                "p_merchant_name",
                "//div[@id='offer-display-features']//div[@offer-display-feature-name='desktop-merchant-info'][2]//span//text()",
            ),
            (
                "p_fulfiller_name",
                "//div[@id='offer-display-features']//div[@offer-display-feature-name='desktop-fulfiller-info'][2]//span//text()",
            ),
            (
                "p_bestseller_rank",
                "//div[@id='productDetails_db_sections']//table[@id='productDetails_detailBullets_sections1']//th[contains(text(), 'Best')]/following-sibling::td/span",
            ),
            ("p_bestseller_rank", "//div[@id='detailBulletsWrapper_feature_div']/ul[1]/li/span[@class='a-list-item']"),
        ]

    def read_scraping_infos(self):
        filepath = "../res/mock_urls.csv"
        try:
            with open(filepath, "r") as f:
                csv_reader = csv.reader(f, delimiter=';')
                next(csv_reader)
                return [AmazonScrapingInfo(*row) for row in csv_reader if row]
        except IOError as e:
            self.logger.error(f"Error reading file: {e}")
            return []

    def start_requests(self) -> Request:
        for scraping_info in self.scraping_infos:
            scraping_info.request_timestamp = datetime.now()
            yield scrapy.Request(
                url=scraping_info.url, callback=self.parse_search_page, meta={"scraping_info": scraping_info}
            )

    def parse_search_page(self, response: Response) -> AmazonItem:
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

            # if product_url contains "sspa" get only the link

            if product_url:
                url = product_url[0].get()
                if url is not None:
                    if "sspa" in url:
                        url = "/dp/" + amazon_item.asin
                    amazon_item.p_url = url
                    yield response.follow(
                        url,
                        callback=self.parse_product_page,
                        meta={"amazon_item": amazon_item, "fallback_item": amazon_item, "handle_httpstatus_all": True},
                        errback=self.handle_request_failure,
                    )

            else:
                yield amazon_item

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

    def load_amazon_search_item(self, response: Response, scraping_info: AmazonScrapingInfo) -> AmazonItem:
        item_loader = AmazonItemLoader(item=AmazonItem(), selector=response)

        # Dynamic loading of fields based on mappings
        for field, xpath in self.get_search_item_field_mappings().items():
            item_loader.add_xpath(field, xpath)

        # Scraping info
        if scraping_info:
            item_loader.add_value("prefix", scraping_info.prefix)
            item_loader.add_value("suffix", scraping_info.suffix)
            item_loader.add_value("url", scraping_info.url)
            item_loader.add_value("request_timestamp", scraping_info.request_timestamp)

        item_loader.add_value(
            "s_display", "list" if (int('sg-col-20-of-24' in response.xpath("@class").get())) else "grid"
        )
        amazonItem = item_loader.load_item()
        amazonItem.image_urls = [amazonItem.image_urls]  # ImagePipeline expects a list

        return amazonItem

    def load_amazon_product_page(self, amazon_item: AmazonItem, response: Response) -> AmazonItem:
        item_loader = AmazonItemLoader(item=amazon_item, selector=response)
        item_loader.add_value("p_url", response.url)

        buy_box_element = response.xpath("//div[@id='offer-display-features']")

        if buy_box_element:
            for field, xpath in self.get_product_page_field_mappings():
                item_loader.add_xpath(field, xpath)

        amazonItem = item_loader.load_item()
        amazonItem.image_urls = [amazonItem.image_urls]  # ImagePipeline expects a list

        return amazonItem
