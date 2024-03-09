import json
import os
import time

from app.common import COLORS, MENU, templates
from app.library.config import configs, toDict
from app.library.models import (MeituAlbum, MeituAlbumTag, MeituCategory,
                                MeituContent, MeituImage, MeituModel,
                                MeituOrganize, MeituTag, session_scope)
from app.library.page import Page, PageAll, get_page_index
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func
from sqlalchemy.sql import text
from starlette.responses import RedirectResponse, Response

# from sqlalchemy.engine.row import Row





router = APIRouter()

@router.get('/handsome', response_class=HTMLResponse)
async def handsome(request: Request, page = "1", order = "new"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituAlbum.id)).filter(MeituAlbum.category_name == 'handsome', MeituAlbum.is_enabled == 1).scalar()
        page = Page(rows, page_index)

        order_by = "view_count" if order == "hot" else "origin_created_at"
        sql = text(f"select meitu_album.*, meitu_model.title as model_title from meitu_album left join meitu_model on meitu_album.model_name = meitu_model.name where meitu_album.category_name = 'handsome' and meitu_album.is_enabled = 1 order by meitu_album.{order_by} desc limit {page.limit} offset {page.offset}")
        albums = session.execute(sql).fetchall()


        if request.state.user_agent.is_mobile:
            sql = text("""select meitu_album.*, meitu_model.title as model_title,
                (select meitu_image.backup_url from meitu_image where meitu_image.album_id = meitu_album.id order by meitu_image.id limit 1) as image_url
                from meitu_album
                left join meitu_model on meitu_album.model_name = meitu_model.name
                where meitu_album.category_name = 'handsome' and meitu_album.is_enabled = 1 order by meitu_album.view_count desc limit 10""")
            tops = session.execute(sql).fetchall()
        else:
            tops = []

    data ={
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "albums": albums,
        "tops": tops
    }
    return templates.TemplateResponse("handsome.html", {"request": request, "data": data})

@router.get('/handsome/{name}', response_class=HTMLResponse)
async def handsome_detail(request: Request, name, page="1"):
    if not name:
        return RedirectResponse("/handsome")

    page_index = get_page_index(page)
    with session_scope() as session:
        # album = session.query(MeituAlbum).filter(MeituAlbum.name == name, MeituAlbum.is_enabled == 1).first()
        sql = text("""select meitu_album.*, meitu_model.title as model_title from meitu_album
                    left join meitu_model on meitu_album.model_name = meitu_model.name
                    where meitu_album.category_name = 'handsome' and meitu_album.name = :name and meitu_album.is_enabled = 1""")
        album = session.execute(sql, {'name':name}).fetchone()
        if not album:
            return RedirectResponse("/404")
        album = toDict(album._asdict())
        album.tags = []
        album.keywords = [album.model_title if album.model_title else album.model_name]

        sql = text("select meitu_tag.* from meitu_album_tag inner join meitu_tag on meitu_album_tag.tag_id = meitu_tag.id where meitu_album_tag.album_id=:album_id")
        tags = session.execute(sql, {'album_id': album.id}).fetchall()
        for tag in tags:
            tag = toDict(tag._asdict())
            tag.color = COLORS[tag.id % len(COLORS)]
            album.tags.append(tag)
            album.keywords.append(tag.title)

        album.meta_keywords = ','.join([x for x in album.keywords if x]) if album.keywords else ''
        rows = session.query(func.count(MeituImage.id)).filter(MeituImage.album_id == album.id, MeituImage.is_enabled == 1).scalar()
        page = PageAll(rows, page_index, page_size=3)
        album.images = session.query(MeituImage).filter(MeituImage.album_id == album.id, MeituImage.is_enabled == 1).limit(page.limit).offset(page.offset).all()

        # related album
        # https://stackoverflow.com/questions/2142922/mysql-select-related-objects-by-tags
        sql = text("""SELECT album.id, album.name, album.title, album.cover, album.model_name, album.origin_created_at, album.view_count, model.title as model_title, COUNT(1) AS tag_count
            FROM meitu_album_tag T1
            JOIN meitu_album_tag T2
            ON T1.tag_id = T2.tag_id AND T1.album_id != T2.album_id
            JOIN meitu_album album ON T2.album_id = album.id
            LEFT JOIN meitu_model model ON album.model_name = model.name
            WHERE album.category_name = 'handsome' AND T1.album_id = :album_id
            GROUP BY T2.album_id
            ORDER BY tag_count DESC
            limit 20;""")
        album.related = session.execute(sql, {'album_id': album.id}).fetchall()
        # album.related = []
        # for item in related:
        #     album.related.append(toDict(item._asdict()))

    data = {
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "album": album
    }
    return templates.TemplateResponse("handsome-detail.html", {"request": request, "data": data})
