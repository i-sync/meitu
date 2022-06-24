import re, json
import scrapy
from meitu.items import MeituModelItem
from bs4 import BeautifulSoup


class ModelSpider(scrapy.Spider):
    name = 'model'

    base_url = "https://www.meijuntu.com"
    start_urls = ['https://www.meijuntu.com/model/']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'meitu.middlewares.MeituModelMiddleware': 500,
            #'xiuren.middlewares.XiurenProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu.pipelines.MeituModelPipeline': 300,
        }
    }


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"page_number": 1})

    def parse(self, response):
        links = response.xpath("//ul[@id='list']/li/a")

        for l in links:
            item = MeituModelItem()
            link = l.xpath("@href").extract_first().strip()
            name = link.split('/')[-1].split('.')[0]
            item["name"] = name
            item["title"] = l.xpath("./p/text()").extract_first().strip()
            item["cover"] = l.xpath("./img/@src").extract_first().strip()
            
            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.detail_parse, meta={"item": item, "request_type": "model", "model_name": name })
            

        page_number = response.meta["page_number"] if "page_number" in response.meta else 1
        page_number += 1
        #if page_number <= last_page:
        if page_number <= 100:
            next_url = f"{self.base_url}/model/index-{page_number}.html"
            print(page_number, "next page", next_url)
            yield scrapy.Request(url = next_url, callback=self.parse, meta={"page_number": page_number})

    def detail_parse(self, response):
        
        # time.sleep(random.random())
        item = response.meta["item"]
        spans = response.xpath("//div[@class='album_info']/div[@class='people-info']/span")
        summary = {}
        for span in spans:
            span = span.xpath("text()").extract_first()
            if span.find(':') > -1 or span.find('：') > -1:
                key, value = re.split(r':|：', span, maxsplit=1)
                key = key.strip()
                value = value.strip()
                if key:
                    summary[key] = value

        description = response.xpath("//div[@class='album_info']/div[@class='album_description']").get()
        description = BeautifulSoup(description, parser='lxml').text.strip() if description else ""
        #description = "".join(description) if description else response.xpath("//div[@class='album_info']/div[@class='album_description']/text()").extract_first()


        item["summary"] = json.dumps(summary, ensure_ascii=False) if summary else ""
        item["description"] = description

        yield item