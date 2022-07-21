# coding=UTF-8
import os
import sys

sys.path.append('../')
from app.library.config import configs
from app.library.models import session_scope, MeituAlbum, MeituMedia, MeituModel, MeituOrganize, MeituTag


def generate_sitemap_beauty():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    # category
    with session_scope() as session:
        albums = session.query(MeituAlbum).filter(MeituAlbum.category_name == 'beauty', MeituAlbum.is_enabled == 1).all()
        for album in albums:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/{album.category_name}/{album.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap-beauty.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)

def generate_sitemap_handsome():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    # category
    with session_scope() as session:
        albums = session.query(MeituAlbum).filter(MeituAlbum.category_name == 'handsome', MeituAlbum.is_enabled == 1).all()
        for album in albums:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/{album.category_name}/{album.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap-handsome.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)

def generate_sitemap_news():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    # category
    with session_scope() as session:
        medias = session.query(MeituMedia).filter(MeituMedia.category_name == 'news', MeituMedia.is_enabled == 1).all()
        for media in medias:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/{media.category_name}/{media.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap-news.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)

def generate_sitemap_street():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    # category
    with session_scope() as session:
        medias = session.query(MeituMedia).filter(MeituMedia.category_name == 'street', MeituMedia.is_enabled == 1).all()
        for media in medias:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/{media.category_name}/{media.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap-street.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)

def generate_sitemap_model():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    # category
    with session_scope() as session:
        models = session.query(MeituModel).filter(MeituModel.is_enabled == 1).all()
        for model in models:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/model/{model.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap-model.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)

def generate_sitemap_organize():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    # category
    with session_scope() as session:
        organizes = session.query(MeituOrganize).filter(MeituOrganize.is_enabled == 1).all()
        for organize in organizes:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/organize/{organize.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap-organize.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)


def generate_sitemap_tags():
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    # category
    with session_scope() as session:
        tags = session.query(MeituTag).filter(MeituTag.is_enabled == 1).all()
        for tag in tags:
            item = f'''
    <url>
        <loc>{configs.meta.site_url}/tags/{tag.name}</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
            sitemap += item

    sitemap += '''
</urlset>'''

    with open("../sitemap-tags.xml", "w+", encoding="utf-8") as f:
        f.writelines(sitemap)

if __name__ == "__main__":
    generate_sitemap_beauty()
    generate_sitemap_handsome()
    generate_sitemap_news()
    generate_sitemap_street()
    generate_sitemap_model()
    generate_sitemap_organize()
    generate_sitemap_tags()