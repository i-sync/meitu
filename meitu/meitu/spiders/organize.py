import re, json
import scrapy
from meitu.items import MeituOrganizeItem
from bs4 import BeautifulSoup

class OrganizeSpider(scrapy.Spider):
    name = 'organize'
    base_url = "https://www.meijuntu.com"
    start_urls = ['http://www.meijuntu.com/xzjg/']


    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'meitu.middlewares.MeituOrganizeMiddleware': 500,
            #'xiuren.middlewares.XiurenProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu.pipelines.MeituOrganizePipeline': 300,
        }
    }


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"page_number": 1})

    def parse(self, response):
        links = response.xpath("//ul[@id='list']/li/a")

        for l in links:
            item = MeituOrganizeItem()
            link = l.xpath("@href").extract_first().strip()
            name = link.split('/')[-1].split('.')[0]
            item["name"] = name
            item["title"] = l.xpath("./p/text()").extract_first().strip()
            cover = l.xpath("./img/@src").extract_first()
            item["cover"] = f"{self.base_url}{cover}" if cover and cover.startswith("/") else cover

            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.detail_parse, meta={"item": item, "request_type": "organize", "organize_name": name })
            # break


        page_number = response.meta["page_number"] if "page_number" in response.meta else 1
        page_number += 1
        #if page_number <= last_page:
        if page_number <= 20:
            next_url = f"{self.base_url}/xzjg/index-{page_number}.html"
            print(page_number, "next page", next_url)
            yield scrapy.Request(url = next_url, callback=self.parse, meta={"page_number": page_number})

    def detail_parse(self, response):

        # time.sleep(random.random())
        item = response.meta["item"]
        summary = response.xpath("//div[@class='album_info']/h1/text()").extract_first().strip()
        description = response.xpath("//div[@class='album_info']/div[@class='album_description']").get()
        description = BeautifulSoup(description, parser='lxml').text.strip() if description else ""


        item["summary"] = summary
        item["description"] = description

        yield item
