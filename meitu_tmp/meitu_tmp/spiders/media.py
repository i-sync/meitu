import scrapy
import sys
sys.path.append("..")

from app.library.models import session_scope, MeituModel, MeituOrganize, MeituAlbum, MeituAlbumTag, MeituImage, MeituContent, MeituCategory, MeituTag

from app.library.models import MeituMedia, MeituMediaModel, MeituMediaTag, MeituTmpModel

class MediaSpider(scrapy.Spider):
    name = 'media'
    allowed_domains = ['example.com']
    start_urls = ['http://example.com/']

    default_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "junmeitu.com"
    }

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 'meitu.middlewares.MeituAlbumMiddleware': 500,
            # 'meitu.middlewares.MeituProxyMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'meitu_tmp.pipelines.DownloadMediaImagesPipeline': 300,
        }
    }


    def __init__(self):

        with session_scope() as session:
            # 从数据库中获取cover字段，并添加到start_urls
            models = session.query(MeituMedia).filter(MeituMedia.cover_backup == None, MeituMedia.cover.like('http%')).limit(10).all()
            self.start_urls = [(model.id, model.cover) for model in models]


    def start_requests(self):
        for id, url in self.start_urls:
            yield scrapy.Request(url, headers = self.default_headers, meta={'id': id})


    def parse(self, response):
        # 检查响应状态码
        if response.status != 200:
            self.log('Failed to download image %s, status code: %d' % (response.url, response.status))
            return
        yield {'image_content': response.body, 'image_url': response.url, 'id': response.meta['id']}

