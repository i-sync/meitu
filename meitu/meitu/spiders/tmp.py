import time
import scrapy

from meitu.items import MeituTmpItem
from bs4 import BeautifulSoup


class TmpSpider(scrapy.Spider):
    name = 'tmp'

    base_url = "https://www.meijuntu.com"
    start_urls = ['https://www.meijuntu.com/news']

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
            item = MeituTmpItem()
            item["category_name"] = "news"
            link = l.xpath("@href").extract_first().strip()
            name = link.split('/')[-1].split('.')[0]
            # item["name"] = name
            # item["origin_link"] = f"{self.base_url}{link}"
            #item["title"] = l.xpath("./p/text()").extract_first().strip()

            cover = l.xpath("./img/@src").extract_first().strip()
            # item["cover"] = f"{self.base_url}{cover}" if cover and cover.startswith("/") else cover

            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.detail_parse, meta={"item": item, "request_type": "media", "category_name": "news", "media_name": name })
            # break

        page_number = response.meta["page_number"] if "page_number" in response.meta else 1
        page_number += 1
        #if page_number <= last_page:
        if page_number <= 57:
            next_url = f"{self.base_url}/news/index-{page_number}.html"
            print(page_number, "next page", next_url)
            yield scrapy.Request(url = next_url, callback=self.parse, meta={"page_number": page_number})

    def detail_parse(self, response):

        # time.sleep(random.random())
        item = response.meta["item"]

        item["models"] = []
        tags = response.xpath("//div[@class='main']/div[@class='news-content fl']/div[@class='relation_tags']/a")
        for tag in tags:
            l = tag.xpath("./@href").extract_first().strip()


            tag_type = l.split('/')[-2].strip().lower()
            if tag_type == "model":
                name = l.split('/')[-1].split('.')[0]
                item["models"].append({"name": name, "model_url": f"{self.base_url}{l}"})

        yield item
