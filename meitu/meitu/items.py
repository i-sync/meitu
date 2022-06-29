# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MeituModelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    description = scrapy.Field()
    cover = scrapy.Field()


class MeituOrganizeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    description = scrapy.Field()
    cover = scrapy.Field()

class MeituTagItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    description = scrapy.Field()
    cover = scrapy.Field()


class MeituAblumItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    model_name = scrapy.Field()
    organize_name = scrapy.Field()
    category_name = scrapy.Field()

    name = scrapy.Field()
    title = scrapy.Field()
    #summary = scrapy.Field()
    description = scrapy.Field()
    cover = scrapy.Field()
    origin_link = scrapy.Field()
    origin_created_at = scrapy.Field()

    #sub table
    tags = scrapy.Field()
    images_url = scrapy.Field()
    contents = scrapy.Field()


class MeituMediaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    keywords = scrapy.Field()
    model_name = scrapy.Field()
    category_name = scrapy.Field()

    name = scrapy.Field()
    title = scrapy.Field()
    #summary = scrapy.Field()
    description = scrapy.Field()
    cover = scrapy.Field()
    origin_link = scrapy.Field()
    origin_created_at = scrapy.Field()

    #sub table
    tags = scrapy.Field()
    contents = scrapy.Field()


class MeituTmpItem(MeituMediaItem):
    models = scrapy.Field()