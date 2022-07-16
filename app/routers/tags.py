import os, json, time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy import func, desc
from sqlalchemy.sql import text
# from sqlalchemy.engine.row import Row

from starlette.responses import Response, RedirectResponse

from app.common import MENU, COLORS, templates
from app.library.models import session_scope, MeituAlbum, MeituAlbumTag, MeituMedia, MeituMediaTag, MeituCategory, MeituContent, MeituImage, MeituModel, MeituOrganize, MeituTag
from app.library.models import MeituMediaModel
from app.library.page import Page, PageAll, get_page_index
from app.library.config import toDict, configs



router = APIRouter()

@router.get('/tags', response_class=HTMLResponse)
async def tags(request: Request, page = "1"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituTag.id)).filter(MeituTag.is_enabled == 1).scalar()
        page = Page(rows, page_index)

        tags = session.query(MeituTag).filter(MeituTag.is_enabled == 1).limit(page.limit).offset(page.offset).all()

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
    if not name:
        return RedirectResponse("/tags")

    page_index = get_page_index(page)
    with session_scope() as session:
        tag = session.query(MeituTag).filter(MeituTag.name == name, MeituTag.is_enabled == 1).first()
        if not tag:
            return RedirectResponse("/404")

        albums = medias = []
        if category_name == "beauty" or category_name == "handsome":
            rows = session.query(func.count(MeituAlbum.id)).join(MeituAlbumTag, MeituAlbum.id == MeituAlbumTag.album_id).filter(MeituAlbum.category_name == category_name, MeituAlbum.is_enabled == 1, MeituAlbumTag.tag_id == tag.id).scalar()
            page = Page(rows, page_index)
            albums = session.query(MeituAlbum).join(MeituAlbumTag, MeituAlbum.id == MeituAlbumTag.album_id).filter(MeituAlbum.category_name == category_name, MeituAlbum.is_enabled == 1, MeituAlbumTag.tag_id == tag.id).limit(page.limit).offset(page.offset).all()
        elif category_name == "news" or category_name == "street":
            rows = session.query(func.count(MeituMedia.id)).join(MeituMediaTag, MeituMedia.id == MeituMediaTag.media_id).filter(MeituMedia.category_name == category_name, MeituMedia.is_enabled == 1, MeituMediaTag.tag_id == tag.id).scalar()
            page = Page(rows, page_index)
            medias = session.query(MeituMedia).join(MeituMediaTag, MeituMedia.id == MeituMediaTag.media_id).filter(MeituMedia.category_name == category_name, MeituMedia.is_enabled == 1, MeituMediaTag.tag_id == tag.id).limit(page.limit).offset(page.offset).all()
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