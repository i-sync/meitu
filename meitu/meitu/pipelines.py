# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import os, sys, time, json
sys.path.append("..")
from itemadapter import ItemAdapter
from app.library.models import session_scope, MeituModel, MeituOrganize, MeituAlbum, MeituAlbumTag, MeituImage, MeituContent, MeituCategory, MeituTag

from app.library.models import MeituMedia, MeituMediaModel, MeituMediaTag, MeituTmpModel


class MeituPipeline:
    def process_item(self, item, spider):
        return item


class MeituModelPipeline:

    def process_item(self, item, spider):
        print(item)
        model = MeituModel()
        model.name = item["name"]
        model.title = item["title"]
        model.summary = item["summary"]
        model.description = item["description"]
        model.cover = item["cover"]
        model.view_count = 0
        model.created_at = time.time()
        model.is_enabled = 1
        with session_scope() as session:
            session.add(model)
            session.commit()
        return item


class MeituOrganizePipeline:

    def process_item(self, item, spider):
        print(item)
        model = MeituOrganize()
        model.name = item["name"]
        model.title = item["title"]
        model.summary = item["summary"]
        model.description = item["description"]
        model.cover = item["cover"]
        model.view_count = 0
        model.created_at = time.time()
        model.is_enabled = 1
        with session_scope() as session:
            session.add(model)
            session.commit()
        return item

class MeituTagPipeline:

    def process_item(self, item, spider):
        print(item)
        model = MeituTag()
        model.name = item["name"]
        model.title = item["title"]
        model.summary = item["summary"]
        model.description = item["description"]
        model.cover = item["cover"]
        model.created_at = time.time()
        model.view_count = 0
        model.is_enabled = 1
        with session_scope() as session:
            session.add(model)
            session.commit()
        return item

class MeituAlbumPipeline:

    def process_item(self, item, spider):
        # print(item)
        # return
        with session_scope() as session:
            model = session.query(MeituAlbum).filter(MeituAlbum.name == item["name"], MeituAlbum.category_name == item["category_name"]).first()
            if model:
                print(f'albumn already exists, skip. {item["name"]}, {item["title"]}, {item["origin_link"]}')
                return

        model = MeituAlbum()
        model.model_name = item["model_name"] if "model_name" in item else None
        model.organize_name = item["organize_name"] if "organize_name" in item else None

        model.category_name = item["category_name"]
        model.name = item["name"]
        model.title = item["title"]
        #model.summary = item["summary"]
        model.description = item["description"]
        model.cover = item["cover"]
        model.origin_link = item["origin_link"]
        model.origin_created_at = item["origin_created_at"] if "origin_created_at" in item else time.time()


        tags = item["tags"]
        images_url = item["images_url"]
        contents = item["contents"]

        model.created_at = time.time()
        model.updated_at = time.time()
        model.is_enabled = 1
        model.view_count = 0

        with session_scope() as session:
            session.add(model)
            session.flush()
            album_id = model.id

            if len(tags):
                for t in tags:
                    tag = session.query(MeituTag).filter(MeituTag.name == t).first()
                    if tag:
                        album_tag = MeituAlbumTag()
                        album_tag.album_id = album_id
                        album_tag.tag_id = tag.id
                        album_tag.created_at = time.time()
                        session.add(album_tag)
                    else:
                        print(f"tag not found!, album_id:{album_id}, album_name:{model.name}, tag_name:{t}")

            if model.category_name == "beauty" or model.category_name == "handsome":
                # process image table
                for img in images_url:
                    image = MeituImage()
                    image.album_id = album_id
                    image.image_url = img
                    image.created_at = time.time()
                    image.updated_at = time.time()
                    image.is_enabled = 1
                    session.add(image)
            else:
                # process content table
                for con in contents:
                    content = MeituContent()
                    content.album_id = album_id
                    content.content = con
                    content.created_at = time.time()
                    content.updated_at = time.time()
                    content.is_enabled = 1
                    session.add(content)

            # commit
            session.commit()
            print(f"album commit, title: {model.title}")

        return item

class MeituMediaPipeline:

    def process_item(self, item, spider):
        # print(item)
        # return
        with session_scope() as session:
            model = session.query(MeituMedia).filter(MeituMedia.name == item["name"], MeituMedia.category_name == item["category_name"]).first()
            if model:
                print(f'media already exists, skip. {item["name"]}, {item["title"]}, {item["origin_link"]}')
                return

        model = MeituMedia()
        model.keywords = json.dumps(item["keywords"], ensure_ascii=False)

        model.category_name = item["category_name"]
        model.name = item["name"]
        model.title = item["title"]
        #model.summary = item["summary"]
        model.description = item["description"]
        model.cover = item["cover"]
        model.origin_link = item["origin_link"]
        model.origin_created_at = item["origin_created_at"] if "origin_created_at" in item else time.time()


        tags = item["tags"]
        contents = item["contents"]
        model_name = item["model_name"]

        model.created_at = time.time()
        model.updated_at = time.time()
        model.is_enabled = 1
        model.view_count = 0

        with session_scope() as session:
            session.add(model)
            session.flush()
            media_id = model.id

            if len(tags):
                for t in tags:
                    tag = session.query(MeituTag).filter(MeituTag.name == t).first()
                    if tag:
                        media_tag = MeituMediaTag()
                        media_tag.media_id = media_id
                        media_tag.tag_id = tag.id
                        media_tag.created_at = time.time()
                        session.add(media_tag)
                    else:
                        print(f"tag not found!, media_id:{media_id}, media_name:{model.name}, tag_name:{t}")

            if len(model_name):
                for t in model_name:
                    tmp = session.query(MeituModel).filter(MeituModel.name == t).first()
                    if tmp:
                        media_model = MeituMediaModel()
                        media_model.media_id = media_id
                        media_model.model_id = tmp.id
                        media_model.created_at = time.time()
                        session.add(media_model)
                    else:
                        print(f"model not found!, media_id:{media_id}, media_name:{model.name}, model_name:{t}")

            # process content table
            for con in contents:
                content = MeituContent()
                content.media_id = media_id
                content.content = con
                content.created_at = time.time()
                content.updated_at = time.time()
                content.is_enabled = 1
                session.add(content)

            # commit
            session.commit()
            print(f"media commit, title: {model.title}")

        return item



class MeituTmpPipeline:

    def process_item(self, item, spider):
        # print(item)
        # return
        models = item["models"]
        print(models)
        if models and len(models):
            with session_scope() as session:
                for model in models:
                    name = model["name"]
                    model_url = model["model_url"]


                    tmp = session.query(MeituTmpModel).filter(MeituTmpModel.name == name).first()
                    if tmp:
                        print(f'model name already exists, skip. {name}')
                        continue
                    tmp = MeituTmpModel()
                    tmp.name = name
                    tmp.model_url = model_url
                    session.add(tmp)

                #commit
                session.commit()