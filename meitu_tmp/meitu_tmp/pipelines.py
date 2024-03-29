# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

import re
import os
from app.library.models import session_scope, MeituModel, MeituOrganize, MeituAlbum, MeituAlbumTag, MeituImage, MeituContent, MeituCategory, MeituTag

from app.library.models import MeituMedia, MeituMediaModel, MeituMediaTag, MeituTmpModel

class MeituTmpPipeline:
    def process_item(self, item, spider):
        return item


def extract_date_from_url(url):
    # 匹配第一种URL格式
    match = re.search(r'/(\d{4})(\d{2})(\d{2})', url)
    if match:
        return match.groups()

    # 匹配第二种URL格式
    match = re.search(r'/(\d{4})/(\d{2})\d{2}', url)
    if match:
        return match.groups()

    # 匹配第三种URL格式
    match = re.search(r'/(\d{4})/', url)
    if match:
        return match.groups() + ('01', '01')  # 使用默认的月份和日期

    # 如果都不匹配，返回None
    return None, None, None

class DownloadModelImagesPipeline():
    def process_item(self, item, spider):
        if not item:
            print("item no exists!")
            return None
        # 使用下载的图片内容
        image_content = item['image_content']
        image_url = item['image_url']

        # 测试
        year, month, day = extract_date_from_url(image_url)
        # print(year, month, day)  # 输出：2022 01 01
        if not year:
            year, month, day = ('1970', '01', '01')

        image_path = os.path.join(year, month, day, image_url.split('/')[-1])
        print(image_url, image_path)

        IMAGES_STORE = spider.settings.get("IMAGES_STORE", '/mnt/hdd/meitu/images')
        # print(IMAGES_STORE)
        # 创建文件夹
        os.makedirs(os.path.join(IMAGES_STORE, year, month, day), exist_ok=True)

        # print(os.path.join(IMAGES_STORE, image_path))
        # 存储图片
        with open(os.path.join(IMAGES_STORE, image_path), 'wb') as f:
            f.write(image_content)

        with session_scope() as session:
            session.query(MeituModel).filter(MeituModel.id == item['id']).update({MeituModel.cover_backup : os.path.join('/static/images',image_path)}, synchronize_session = False)
            session.commit()

class DownloadOrganizeImagesPipeline():
    def process_item(self, item, spider):
        if not item:
            print("item no exists!")
            return None
        # 使用下载的图片内容
        image_content = item['image_content']
        image_url = item['image_url']

        # 测试
        year, month, day = extract_date_from_url(image_url)
        # print(year, month, day)  # 输出：2022 01 01
        if not year:
            year, month, day = ('1970', '01', '01')

        image_path = os.path.join(year, month, day, image_url.split('/')[-1])
        print(image_url, image_path)

        IMAGES_STORE = spider.settings.get("IMAGES_STORE", '/mnt/hdd/meitu/images')
        # print(IMAGES_STORE)
        # 创建文件夹
        os.makedirs(os.path.join(IMAGES_STORE, year, month, day), exist_ok=True)

        # print(os.path.join(IMAGES_STORE, image_path))
        # 存储图片
        with open(os.path.join(IMAGES_STORE, image_path), 'wb') as f:
            f.write(image_content)

        with session_scope() as session:
            session.query(MeituOrganize).filter(MeituOrganize.id == item['id']).update({MeituOrganize.cover_backup : os.path.join('/static/images',image_path)}, synchronize_session = False)
            session.commit()


class DownloadTagImagesPipeline():
    def process_item(self, item, spider):
        if not item:
            print("item no exists!")
            return None
        # 使用下载的图片内容
        image_content = item['image_content']
        image_url = item['image_url']

        # 测试
        year, month, day = extract_date_from_url(image_url)
        # print(year, month, day)  # 输出：2022 01 01
        if not year:
            year, month, day = ('1970', '01', '01')

        image_path = os.path.join(year, month, day, image_url.split('/')[-1])
        print(image_url, image_path)

        IMAGES_STORE = spider.settings.get("IMAGES_STORE", '/mnt/hdd/meitu/images')
        # print(IMAGES_STORE)
        # 创建文件夹
        os.makedirs(os.path.join(IMAGES_STORE, year, month, day), exist_ok=True)

        # print(os.path.join(IMAGES_STORE, image_path))
        # 存储图片
        with open(os.path.join(IMAGES_STORE, image_path), 'wb') as f:
            f.write(image_content)

        with session_scope() as session:
            session.query(MeituTag).filter(MeituTag.id == item['id']).update({MeituTag.cover_backup : os.path.join('/static/images',image_path)}, synchronize_session = False)
            session.commit()


class DownloadAlbumImagesPipeline():
    def process_item(self, item, spider):
        if not item:
            print("item no exists!")
            return None
        # 使用下载的图片内容
        image_content = item['image_content']
        image_url = item['image_url']

        # 测试
        year, month, day = extract_date_from_url(image_url)
        # print(year, month, day)  # 输出：2022 01 01
        if not year:
            year, month, day = ('1970', '01', '01')

        image_path = os.path.join(year, month, day, image_url.split('/')[-1])
        print(image_url, image_path)

        IMAGES_STORE = spider.settings.get("IMAGES_STORE", '/mnt/hdd/meitu/images')
        # print(IMAGES_STORE)
        # 创建文件夹
        os.makedirs(os.path.join(IMAGES_STORE, year, month, day), exist_ok=True)

        # print(os.path.join(IMAGES_STORE, image_path))
        # 存储图片
        with open(os.path.join(IMAGES_STORE, image_path), 'wb') as f:
            f.write(image_content)

        with session_scope() as session:
            session.query(MeituAlbum).filter(MeituAlbum.id == item['id']).update({MeituAlbum.cover_backup : os.path.join('/static/images',image_path)}, synchronize_session = False)
            session.commit()



class DownloadImageImagesPipeline():
    def process_item(self, item, spider):
        if not item:
            print("item no exists!")
            return None
        # 使用下载的图片内容
        image_content = item['image_content']
        image_url = item['image_url']

        # 测试
        year, month, day = extract_date_from_url(image_url)
        # print(year, month, day)  # 输出：2022 01 01
        if not year:
            year, month, day = ('1970', '01', '01')

        image_path = os.path.join(year, month, day, image_url.split('/')[-1])
        print(image_url, image_path)

        IMAGES_STORE = spider.settings.get("IMAGES_STORE", '/mnt/hdd/meitu/images')
        # print(IMAGES_STORE)
        # 创建文件夹
        os.makedirs(os.path.join(IMAGES_STORE, year, month, day), exist_ok=True)

        # print(os.path.join(IMAGES_STORE, image_path))
        # 存储图片
        with open(os.path.join(IMAGES_STORE, image_path), 'wb') as f:
            f.write(image_content)

        with session_scope() as session:
            session.query(MeituImage).filter(MeituImage.id == item['id']).update({MeituImage.backup_url : os.path.join('/static/images',image_path)}, synchronize_session = False)
            session.commit()


class DownloadMediaImagesPipeline():
    def process_item(self, item, spider):
        if not item:
            print("item no exists!")
            return None
        # 使用下载的图片内容
        image_content = item['image_content']
        image_url = item['image_url']

        # 测试
        year, month, day = extract_date_from_url(image_url)
        # print(year, month, day)  # 输出：2022 01 01
        if not year:
            year, month, day = ('1970', '01', '01')

        image_path = os.path.join(year, month, day, image_url.split('/')[-1])
        print(image_url, image_path)

        IMAGES_STORE = spider.settings.get("IMAGES_STORE", '/mnt/hdd/meitu/images')
        # print(IMAGES_STORE)
        # 创建文件夹
        os.makedirs(os.path.join(IMAGES_STORE, year, month, day), exist_ok=True)

        # print(os.path.join(IMAGES_STORE, image_path))
        # 存储图片
        with open(os.path.join(IMAGES_STORE, image_path), 'wb') as f:
            f.write(image_content)

        with session_scope() as session:
            session.query(MeituMedia).filter(MeituMedia.id == item['id']).update({MeituMedia.cover_backup : os.path.join('/static/images',image_path)}, synchronize_session = False)
            session.commit()


class ContentImagePipeline(ImagesPipeline):
    default_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "junmeitu.com"
    }

    def file_path(self, request, response=None, info=None, *, item=None):

        image_url = request.url
        # 测试
        year, month, day = extract_date_from_url(image_url)
        # print(year, month, day)  # 输出：2022 01 01
        if not year:
            year, month, day = ('1970', '01', '01')

        image_path = os.path.join(year, month, day, image_url.split('/')[-1])

        return image_path

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url, headers=self.default_headers)

    def item_completed(self, results, item, info):
        image_paths = [x for ok, x in results if ok]
        #print(image_paths)
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item


class DownloadContentImagesPipeline():
    def process_item(self, item, spider):
        if not item:
            print("item no exists!")
            return None


        with session_scope() as session:
            session.query(MeituContent).filter(MeituContent.id == item['id']).update({MeituContent.content_backup : item['content_backup']}, synchronize_session = False)
            session.commit()

        return item