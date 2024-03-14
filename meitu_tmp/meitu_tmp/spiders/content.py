import os
import scrapy
import sys
sys.path.append("..")

from app.library.models import session_scope, MeituModel, MeituOrganize, MeituAlbum, MeituAlbumTag, MeituImage, MeituContent, MeituCategory, MeituTag

from app.library.models import MeituMedia, MeituMediaModel, MeituMediaTag, MeituTmpModel

from bs4 import BeautifulSoup

from meitu_tmp.pipelines import extract_date_from_url
from meitu_tmp.items import MeituContentItem

class ContentSpider(scrapy.Spider):
    name = 'content'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    default_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "junmeitu.com"
    }

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'meitu_tmp.middlewares.MeituTmpIgnoreDownloaderMiddleware': 1,
            # 'meitu.middlewares.MeituProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu_tmp.pipelines.ContentImagePipeline': 200,
            'meitu_tmp.pipelines.DownloadContentImagesPipeline': 300,
        }
    }


    def start_requests(self):

        with session_scope() as session:
            # 从数据库中获取cover字段，并添加到start_urls
            models = session.query(MeituContent.id, MeituContent.content).filter(MeituContent.content_backup == None).limit(3).all()
            for model in models:
                page_content = BeautifulSoup(model.content, 'html.parser')
                images = page_content.find_all("img")
                image_urls = []
                for img in images:

                    del img["referrerpolicy"]
                    # 2/3 change src -> data-src and src -> cartoon-snail-loading-loading-gif-animation_2734139.png
                    img_src = img.get("data-src")
                    image_urls.append(img_src)

                    year, month, day = extract_date_from_url(img_src)
                    # print(year, month, day)  # 输出：2022 01 01
                    if not year:
                        year, month, day = ('1970', '01', '01')

                    image_path = os.path.join('/static/images', year, month, day, img_src.split('/')[-1])
                    #print(model.id, img_src, image_path)
                    img["data-src"] = image_path
                    img["src"] = "/static/imgs/loading.gif"

                content_backup = str(page_content)
                # yield {"id": model.id, "image_urls": image_urls, "content_backup": content_backup}

                yield scrapy.Request(url=f'http://www.example.com/{model.id}', callback=self.parse, meta={"id": model.id, "image_urls": image_urls, "content_backup": content_backup})

    def parse(self, response):
        item = MeituContentItem()
        item['id'] = response.meta['id']
        item['image_urls'] = response.meta['image_urls']
        item['content_backup'] = response.meta['content_backup']
        yield item