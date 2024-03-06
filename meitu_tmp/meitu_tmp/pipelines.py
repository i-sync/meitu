# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import re
import os
from app.library.models import session_scope, MeituModel, MeituOrganize, MeituAlbum, MeituAlbumTag, MeituImage, MeituContent, MeituCategory, MeituTag


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