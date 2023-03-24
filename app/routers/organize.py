import json
import os
import time

from app.common import COLORS, MENU, templates
from app.library.config import configs, toDict
from app.library.models import (MeituAlbum, MeituCategory, MeituContent,
                                MeituImage, MeituMedia, MeituMediaModel,
                                MeituMediaTag, MeituOrganize, MeituTag,
                                session_scope)
from app.library.page import Page, PageAll, get_page_index
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func
from sqlalchemy.sql import text
from starlette.responses import RedirectResponse, Response

# from sqlalchemy.engine.row import Row



router = APIRouter()

@router.get('/organize', response_class=HTMLResponse)
async def organize(request: Request, page = "1"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituOrganize.id)).filter(MeituOrganize.is_enabled == 1).scalar()
        page = Page(rows, page_index)

        sql = f"""select meitu_organize.*, count(meitu_album.id) as organize_count from meitu_organize
                    left join meitu_album on meitu_organize.name = meitu_album.organize_name
                    group by meitu_organize.id
                    order by organize_count desc limit {page.limit} offset {page.offset}"""
        organizes = session.execute(sql).fetchall()

    data ={
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "organizes": organizes
    }
    return templates.TemplateResponse("organize.html", {"request": request, "data": data})

@router.get('/organize/{name}', response_class=HTMLResponse)
async def organize_detail(request: Request, name, page="1"):
    if not name:
        return RedirectResponse("/organize")

    page_index = get_page_index(page)
    with session_scope() as session:
        organize = session.query(MeituOrganize).filter(MeituOrganize.name == name, MeituOrganize.is_enabled == 1).first()

        if not organize:
            return RedirectResponse("/404")

        rows = session.query(func.count(MeituAlbum.id)).filter(MeituAlbum.organize_name == organize.name, MeituAlbum.is_enabled == 1).scalar()
        page = Page(rows, page_index)
        albums = session.query(MeituAlbum).filter(MeituAlbum.organize_name == organize.name, MeituAlbum.is_enabled == 1).limit(page.limit).offset(page.offset).all()

    data = {
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "organize": organize,
        "albums": albums
    }

    return templates.TemplateResponse("organize-detail.html", {"request": request, "data": data})
