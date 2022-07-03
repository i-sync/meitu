import time
import scrapy

from meitu.items import MeituMediaItem
from bs4 import BeautifulSoup


class StreetSpider(scrapy.Spider):
    name = 'street'

    #allowed_domains = ['www.meijuntu.com']
    base_url = "https://www.meijuntu.com"
    start_urls = ['https://www.meijuntu.com/street']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'meitu.middlewares.MeituMediaMiddleware': 500,
            'meitu.middlewares.MeituProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu.pipelines.MeituMediaPipeline': 300,
        }
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"page_number": 1})

    def parse(self, response):
        links = response.xpath("//ul[@id='list']/li/a")

        for l in links:
            item = MeituMediaItem()
            item["category_name"] = "street"
            link = l.xpath("@href").extract_first().strip()
            name = link.split('/')[-1].split('.')[0]
            item["name"] = name
            item["origin_link"] = f"{self.base_url}{link}"
            #item["title"] = l.xpath("./p/text()").extract_first().strip()

            cover = l.xpath("./img/@src").extract_first().strip()
            item["cover"] = f"{self.base_url}{cover}" if cover and cover.startswith("/") else cover

            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.detail_parse, meta={"item": item, "request_type": "media", "category_name": "street", "media_name": name })
            # break

        page_number = response.meta["page_number"] if "page_number" in response.meta else 1
        page_number += 1
        #if page_number <= last_page:
        if page_number <= 378:
            next_url = f"{self.base_url}/street/index-{page_number}.html"
            print(page_number, "next page", next_url)
            yield scrapy.Request(url = next_url, callback=self.parse, meta={"page_number": page_number})

    def detail_parse(self, response):

        # time.sleep(random.random())
        item = response.meta["item"]

        title = response.xpath("//div[@class='main']/div[@class='news-content fl']/h1[@class='news-title']/text()").extract_first().strip()

        description = response.xpath("/html/head/meta[@name='description']/@content").extract_first()

        origin_date = response.xpath("//div[@class='main']/div[@class='news-content fl']/div[@class='news-info']/span[1]/text()").extract_first()
        if origin_date:
            organize_date = origin_date.split(':')[-1]
            item["origin_created_at"] = time.mktime(time.strptime(organize_date, "%Y-%m-%d"))

        item["model_name"] = []
        item["keywords"] = []
        item["tags"] = []
        tags = response.xpath("//div[@class='main']/div[@class='news-content fl']/div[@class='relation_tags']/a")
        for tag in tags:
            l = tag.xpath("./@href").extract_first().strip()
            t = tag.xpath("./text()").extract_first()
            # skip empty
            if not t:
                continue
            item["keywords"].append(t)

            tag_type = l.split('/')[-2].strip().lower()
            if tag_type == "model":
                name = l.split('/')[-1].split('.')[0]
                item["model_name"].append(name)
            elif tag_type == "tags":
                name = l.split('/')[-1].split('.')[0]
                item["tags"].append(name[:-5])


        item["title"] = title
        item["description"] = description


        item["contents"] = []
        content = response.xpath("//div[@class='main']/div[@class='news-content fl']/div[@class='news-body']").get()
        content = self.update_content(content, title)
        item["contents"].append(content)


        last = response.xpath("//div[@class='main']/div[@class='news-content fl']/div[@class='pages']/a[position() = (last() - 1)]/text()").extract_first()
        if last:
            pages = []
            for index in range(2, int(last.strip())+1):
                pages.append(f'/street/{item["name"]}-{index}.html')
            if len(pages) > 0:
                link = pages.pop(0)
                yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.sub_detail_parse, meta={"item": item, "pages": pages})
            else:
                yield item
        else:
            yield item

    def sub_detail_parse(self, response):
        # time.sleep(random.random())
        item = response.meta["item"]
        pages = response.meta["pages"]

        content = response.xpath("//div[@class='main']/div[@class='news-content fl']/div[@class='news-body']").get()

        content = self.update_content(content, item["title"])
        item["contents"].append(content)

        if len(pages):
            link = pages.pop(0)
            yield scrapy.Request(url = f"{self.base_url}{link}", callback=self.sub_detail_parse, meta={"item": item, "pages": pages})
        else:
            yield item

    def update_content(self, html, title):
        """
            parser content html
            1. remove image style , width, height
            2. change image src attribute to data-src
            3. update image src to `/static/images/loading.gif`
            4. add lazyload class
            5. set referrerpolicy = no-referrer
            6. update image alt to title
        """
        page_content = BeautifulSoup(html, 'html.parser')
        images = page_content.find_all("img")
        for img in images:
            # 1. remove style
            del img["style"]
            del img["width"]
            del img["height"]

            # 2/3 change src -> data-src and src -> loading.gif
            if img.has_attr("data-original"):
                img_src = img.get("data-original")
                del img["data-original"]
            else:
                img_src = img.get("src")
            img["src"] = "/static/images/loading.gif"
            img["data-src"] = img_src

            # 4/5 add lazy class, set referrerpolicy="no-referrer"
            img["referrerpolicy"] = "no-referrer"
            img["class"] = img.get("class", []) + ["lazy"]

            # 6 update image alt to title
            img["alt"] = title

        # print(page_content)
        return str(page_content)
