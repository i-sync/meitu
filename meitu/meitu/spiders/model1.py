import sys
sys.path.append("..")
import re, json
import scrapy
from meitu.items import MeituModelItem
from bs4 import BeautifulSoup

from app.library.models import session_scope, MeituTmpModel


class Model1Spider(scrapy.Spider):
    name = 'model1'

    base_url = "https://www.meijuntu.com"
    start_urls = ['https://www.meijuntu.com/model/']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'meitu.middlewares.MeituModelMiddleware': 500,
            'meitu.middlewares.MeituProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu.pipelines.MeituModelPipeline': 300,
        }
    }


    def start_requests(self):
        with session_scope() as session:
            models = session.query(MeituTmpModel).all()
            for model in models:
                yield scrapy.Request(url=model.model_url, callback=self.parse, meta={"request_type": "model", "model_name": model.name })
                # break


    def parse(self, response):

        # time.sleep(random.random())
        item = MeituModelItem()
        item["name"] = response.meta["model_name"]
        title = response.xpath("//div[@class='album_info']/h1/text()").extract_first().strip()
        item["title"] = title.split('(')[0]
        cover = response.xpath("//div[@class='doujin_album_info mini']/div[@class='thumb']/img/@src").extract_first()
        item["cover"] = cover
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