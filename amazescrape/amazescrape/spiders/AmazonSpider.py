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
                next(csv_reader)
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
        # TODO: what about carousels?

        if not search_results:
            self.logger.warning(f"No search results found on {response.url}")
            return

        self.logger.info(f"Found {len(search_results)} search results on {response.url}")
        scraping_info = response.meta.get('scraping_info')

        for search_result in search_results:
            amazon_item = self.load_amazon_search_item(search_result, scraping_info)
            product_url = search_result.xpath(".//h2//a[contains(@class, 'a-link-normal')]/@href")

            if product_url:
                url = product_url[0].get()
                if url is not None:
                    # follow
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

        # Image URL (add as list)
        item_loader.add_xpath("image_urls", ".//img[@class='s-image']/@src")

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
        item_loader.add_xpath("s_rating_avg", ".//span[@class='a-icon-alt']/text()")
        item_loader.add_xpath("s_rating_n", ".//span[@class='a-size-base s-underline-text']/text()")

        # Price
        item_loader.add_xpath("s_price", ".//span[@class='a-price']/span[@class='a-offscreen']/text()")
        item_loader.add_xpath("s_price_strike", ".//span[@data-a-strike='true']/span/text()")

        # Page ranking
        item_loader.add_xpath("s_rank", "./@data-index")

        # Badges

        ## Status Badge
        item_loader.add_xpath(
            "sb_status_prop", ".//span[@data-component-type='s-status-badge-component']//@data-component-props"
        )
        item_loader.add_xpath(
            "sb_status_text", ".//span[@data-component-type='s-status-badge-component']//@data-csa-c-badge-text"
        )

        ## Amazon Prime
        item_loader.add_xpath("sb_prime", ".//i[contains(@class, 'a-icon-prime')]/@aria-label")

        amazonItem = item_loader.load_item()
        amazonItem.image_urls = [amazonItem.image_urls]  # ImagePipeline expects a list

        return item_loader.load_item()

    def load_amazon_product_page(self, amazon_item: AmazonItem, response: Response) -> AmazonItem:
        item_loader = AmazonItemLoader(item=amazon_item, selector=response)
        item_loader.add_value("p_url", response.url)

        item_loader.add_xpath("p_merchant_id", "//*[@id='merchantID']/@value")

        buy_box_element = response.xpath("//div[@id='offer-display-features']")

        if buy_box_element:
            item_loader.add_xpath(
                "p_fulfiller_name",
                "//div[@id='offer-display-features']//div[@offer-display-feature-name='desktop-fulfiller-info'][2]//span//text()",
            )
            item_loader.add_xpath(
                "p_merchant_name",
                "//div[@id='offer-display-features']//div[@offer-display-feature-name='desktop-merchant-info'][2]//span//text()",
            )

        amazonItem = item_loader.load_item()
        amazonItem.image_urls = [amazonItem.image_urls]  # ImagePipeline expects a list

        return amazonItem
