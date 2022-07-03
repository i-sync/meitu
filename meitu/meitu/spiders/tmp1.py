import time
import scrapy

from meitu.items import MeituTmp1Item
from bs4 import BeautifulSoup

class Tmp1Spider(scrapy.Spider):
    name = 'tmp1'


    base_url = "https://www.meijuntu.com"
    start_urls = ['https://www.meijuntu.com/beauty']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 'meitu.middlewares.MeituMediaMiddleware': 500,
            'meitu.middlewares.MeituProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu.pipelines.MeituTmpPipeline': 300,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"page_number": 1})

    def parse(self, response):
        links = response.xpath("//ul[@id='list']/li/a")

        for l in links:
            item = MeituTmp1Item()
            item["category_name"] = "beauty"
            link = l.xpath("@href").extract_first().strip()
            name = link.split('/')[-1].split('.')[0]
            # item["name"] = name
            # item["origin_link"] = f"{self.base_url}{link}"
            #item["title"] = l.xpath("./p/text()").extract_first().strip()

            # cover = l.xpath("./img/@src").extract_first().strip()
            # item["cover"] = f"{self.base_url}{cover}" if cover and cover.startswith("/") else cover

            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.detail_parse, meta={"item": item, "request_type": "album", "category_name": "beauty", "album_name": name })
            # break

        page_number = response.meta["page_number"] if "page_number" in response.meta else 1
        page_number += 1
        #if page_number <= last_page:
        if page_number <= 1275:
            next_url = f"{self.base_url}/beauty/index-{page_number}.html"
            print(page_number, "next page", next_url)
            yield scrapy.Request(url = next_url, callback=self.parse, meta={"page_number": page_number})

    def detail_parse(self, response):

        # time.sleep(random.random())
        item = response.meta["item"]

        item["models"] = []

        details = response.xpath("//div[@class='main']/div[@class='content']/div[@class='picture-details']")
        models = details.xpath("./span[@class='special'][1]/a")
        for model in models:

            link = model.xpath("@href").extract_first()
            if link and link.split('/')[-2].strip().lower() == "model":
                name = link.split('/')[-1].split('.')[0]
                item["models"].append({"name": name, "model_url": f"{self.base_url}{link}"})

        yield item
