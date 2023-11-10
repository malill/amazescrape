import scrapy


class AmazonSpider(scrapy.Spider):
    name = "amazon"

    def start_requests(self):
        urls = ["https://www.amazon.de/s?k=laptop"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        results  = response.xpath("//div[@data-asin and @data-index and @data-uuid]")
        self.logger.info(f"Found {len(results)} results")
        for res in results:
            yield {"asin": res.xpath("@data-asin").get(), "name": res.xpath(".//h2//text()").get()}
