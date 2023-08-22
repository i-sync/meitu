import json
import os
import time

from app.common import COLORS, MENU, templates
from app.library.config import configs, toDict
from app.library.models import (MeituAlbum, MeituAlbumTag, MeituCategory,
                                MeituContent, MeituImage, MeituMedia,
                                MeituMediaModel, MeituMediaTag, MeituModel,
                                MeituOrganize, MeituTag, session_scope)
from app.library.page import Page, PageAll, get_page_index
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, distinct, func
from sqlalchemy.sql import text
from starlette.responses import RedirectResponse, Response

# from sqlalchemy.engine.row import Row





router = APIRouter()

@router.get('/tags', response_class=HTMLResponse)
async def tags(request: Request, page = "1"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituTag.id)).filter(MeituTag.is_enabled == 1).scalar()
        page = Page(rows, page_index)

        #tags = session.query(MeituTag).filter(MeituTag.is_enabled == 1).limit(page.limit).offset(page.offset).all()
        sql = text(f"""select meitu_tag.*, count(meitu_album_tag.id) as tag_count from meitu_tag
                    left join meitu_album_tag on meitu_tag.id = meitu_album_tag.tag_id
                    where meitu_tag.is_enabled = 1
                    group by meitu_tag.id
                    order by tag_count desc limit {page.limit} offset {page.offset}""")
        tags = session.execute(sql).fetchall()
    data ={
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "tags": tags
    }
    return templates.TemplateResponse("tags.html", {"request": request, "data": data})

@router.get('/tags/{name}', response_class=HTMLResponse)
@router.get('/tags/{name}/{category_name}', response_class=HTMLResponse)
async def tag_detail(request: Request, name, category_name = "beauty", page = "1"):
    """
        https://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression/36141722#36141722
        print sqlchemy raw sql
        q = session.query(func.count(distinct(MeituAlbum.id))).join(MeituAlbumTag, MeituAlbum.id == MeituAlbumTag.album_id).filter(MeituAlbum.category_name == category_name, MeituAlbum.is_enabled == 1).filter((MeituAlbumTag.tag_id == tag.id)|(MeituAlbum.title.contains(name)))
        print(q.statement.compile(compile_kwargs={"literal_binds": True}))
    """
    if not name:
        return RedirectResponse("/tags")

    page_index = get_page_index(page)
    with session_scope() as session:
        tag = session.query(MeituTag).filter(MeituTag.name == name, MeituTag.is_enabled == 1).first()
        if not tag:
            return RedirectResponse("/404")

        albums = medias = []
        if category_name == "beauty" or category_name == "handsome":
            rows = session.query(func.count(distinct(MeituAlbum.id))).join(MeituAlbumTag, MeituAlbum.id == MeituAlbumTag.album_id).filter(MeituAlbum.category_name == category_name, MeituAlbum.is_enabled == 1).filter((MeituAlbumTag.tag_id == tag.id)|(MeituAlbum.title.contains(name))).scalar()
            page = Page(rows, page_index)
            albums = session.query(MeituAlbum).distinct(MeituAlbum.id).join(MeituAlbumTag, MeituAlbum.id == MeituAlbumTag.album_id).filter(MeituAlbum.category_name == category_name, MeituAlbum.is_enabled == 1).filter((MeituAlbumTag.tag_id == tag.id)|(MeituAlbum.title.contains(name))).limit(page.limit).offset(page.offset).all()
        elif category_name == "news" or category_name == "street":
            rows = session.query(func.count(distinct(MeituMedia.id))).join(MeituMediaTag, MeituMedia.id == MeituMediaTag.media_id).filter(MeituMedia.category_name == category_name, MeituMedia.is_enabled == 1).filter((MeituMediaTag.tag_id == tag.id)|(MeituMedia.title.contains(name))).scalar()
            page = Page(rows, page_index)
            medias = session.query(MeituMedia).distinct(MeituMedia.id).join(MeituMediaTag, MeituMedia.id == MeituMediaTag.media_id).filter(MeituMedia.category_name == category_name, MeituMedia.is_enabled == 1).filter((MeituMediaTag.tag_id == tag.id)|(MeituMedia.title.contains(name))).limit(page.limit).offset(page.offset).all()
        else:
            return RedirectResponse("/404")

        categories = session.query(MeituCategory).all()

    data = {
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "category_name": category_name,
        "categories": categories,
        "tag": tag,
        "albums": albums,
        "medias": medias
    }

    return templates.TemplateResponse("tag-detail.html", {"request": request, "data": data})
