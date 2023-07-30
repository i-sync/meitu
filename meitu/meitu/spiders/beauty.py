import time
import scrapy

from meitu.items import MeituAblumItem
from bs4 import BeautifulSoup

class BeautySpider(scrapy.Spider):
    name = 'beauty'

    base_url = "https://www.meijuntu.com"
    start_urls = ['https://www.meijuntu.com/beauty/']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'meitu.middlewares.MeituAlbumMiddleware': 500,
            # 'meitu.middlewares.MeituProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu.pipelines.MeituAlbumPipeline': 300,
        }
    }


    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"page_number": 1})

    def parse(self, response):
        links = response.xpath("//ul[@id='list']/li/a")

        for l in links:
            item = MeituAblumItem()
            item["category_name"] = "beauty"
            link = l.xpath("@href").extract_first().strip()
            name = link.split('/')[-1].split('.')[0]
            item["name"] = name
            item["origin_link"] = f"{self.base_url}{link}"
            item["title"] = l.xpath("./p/text()").extract_first().strip()

            cover = l.xpath("./img/@src").extract_first().strip()
            item["cover"] = f"{self.base_url}{cover}" if cover and cover.startswith("/") else cover

            item["contents"] = []
            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.detail_parse, meta={"item": item, "request_type": "album", "category_name": "beauty", "album_name": name })
            # break

        page_number = response.meta["page_number"] if "page_number" in response.meta else 1
        page_number += 1
        #if page_number <= last_page:
        if page_number <= 3:
            next_url = f"{self.base_url}/beauty/index-{page_number}.html"
            print(page_number, "next page", next_url)
            yield scrapy.Request(url = next_url, callback=self.parse, meta={"page_number": page_number})

    def detail_parse(self, response):

        # time.sleep(random.random())
        item = response.meta["item"]

        title = response.xpath("//div[@class='main']/div[@class='content']/h1[@class='title']/text()").extract_first().strip()
        details = response.xpath("//div[@class='main']/div[@class='content']/div[@class='picture-details']")
        model = details.xpath("./span[@class='special'][1]/a")
        if model:
            link = model.xpath("@href").extract_first()
            if link:
                model_name = link.split('/')[-1].split('.')[0]
            else:
                model_name = model.xpath("text()").extract_first().strip()
            item["model_name"] = model_name

        organize = details.xpath("./span[@class='special'][last()]/a/@href").extract_first()
        if organize:
            organize_name = organize.split('/')[-1].split('.')[0]
            item["organize_name"] = organize_name

        origin_date = details.xpath("./span[last()]/text()").extract_first()
        if origin_date:
            organize_date = origin_date.split(':')[-1]
            item["origin_created_at"] = time.mktime(time.strptime(organize_date, "%Y-%m-%d"))

        item["tags"] = []
        tags = response.xpath("//div[@class='main']/div[@class='content']/div[@class='relation_tags']/a/@href").extract()
        for tag in tags:
            tag = tag.strip()
            tag_name = tag.split('/')[-1].split('.')[0]
            item["tags"].append(tag_name)


        description = response.xpath("//div[@class='main']/div[@class='content']/div[@class='introduce']").get()
        description = BeautifulSoup(description, 'lxml').text.strip() if description else ""

        item["title"] = title
        item["description"] = description

        item["images_url"] = []
        image = response.xpath("//div[@class='main']/div[@class='content']/div[@class='pictures']/img/@src").extract_first().strip()
        item["images_url"].append(image)


        total = response.xpath("//div[@class='main']/div[@class='content']/div[@class='pages']/a[position() = (last() - 1)]/text()").extract_first().strip()
        pages = []
        if total.isdigit():
            for index in range(2, int(total)+1):
                pages.append(f'/beauty/{item["name"]}-{index}.html')
        if len(pages) > 0:
            link = pages.pop(0)
            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.sub_detail_parse, meta={"item": item, "pages": pages})
        else:
            yield item

    def sub_detail_parse(self, response):
        # time.sleep(random.random())
        item = response.meta["item"]
        pages = response.meta["pages"]

        image = response.xpath("//div[@class='main']/div[@class='content']/div[@class='pictures']/img/@src").extract_first().strip()

        item["images_url"].append(image)

        if len(pages):
            link = pages.pop(0)
            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.sub_detail_parse, meta={"item": item, "pages": pages})
        else:
            yield item