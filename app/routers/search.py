import os, json, time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy import func, desc
from sqlalchemy.sql import text
# from sqlalchemy.engine.row import Row

from starlette.responses import Response, RedirectResponse

from app.common import MENU, COLORS, templates
from app.library.models import session_scope, MeituAlbum, MeituMedia, MeituMediaTag, MeituCategory, MeituContent, MeituImage, MeituModel, MeituOrganize, MeituTag
from app.library.models import MeituSearch
from app.library.models import MeituMediaModel
from app.library.page import Page, PageAll, get_page_index
from app.library.config import toDict, configs

router = APIRouter()

@router.get("/search", response_class=HTMLResponse)
async def search(request: Request):

    with session_scope() as session:

        hotlist = session.query(MeituSearch).order_by(desc(MeituSearch.count)).limit(100).all()
        # hotlist = list(range(0, 89))

    data ={
        "menu": MENU,
        "meta": configs.meta,
        "hotlist": hotlist
    }
    return templates.TemplateResponse("search.html", {"request": request, "data": data})

@router.get("/search/{s}", response_class=HTMLResponse)
async def search(s, request: Request, page = "1"):
    if not s:
        return RedirectResponse("/search")

    page_index = get_page_index(page)

    if len(s) > 10:
        albums = models = tags = organizes = []
        data = {
            "menu": MENU,
            "meta": configs.meta,
            "page": page,
            "keyword": s,
            "albums": albums,
            "models": models,
            "tags": tags,
            "organizes": organizes
        }
        return templates.TemplateResponse("search-result.html", {"request": request, "data": data})

    with session_scope() as session:
        search = session.query(MeituSearch).filter(MeituSearch.title == s).first()
        if search:
            search.count += 1
        else:
            search = MeituSearch()
            search.title = s.strip()
            search.count = 0
            search.created_at = time.time()
            session.add(search)
        session.commit()

        # search model
        model = session.query(MeituModel).filter(MeituModel.title == s, MeituModel.is_enabled == 1).first()
        if model:
            return RedirectResponse(f"/model/{model.name}")

        # search tag
        tag = session.query(MeituTag).filter(MeituTag.title == s, MeituTag.is_enabled == 1).first()
        if tag:
            return RedirectResponse(f"/tags/{tag.name}")

        # search organize
        organize = session.query(MeituOrganize).filter(MeituOrganize.title == s, MeituOrganize.is_enabled == 1).first()
        if organize:
            return RedirectResponse(f"/organize/{organize.name}")


        rows = session.query(func.count(MeituAlbum.id)).filter(MeituAlbum.title.contains(s), MeituAlbum.is_enabled == 1).scalar()
        page = Page(rows, page_index)
        if rows:
            #albums = session.query(MeituAlbum).filter(MeituAlbum.title.contains(s), MeituAlbum.is_enabled == 1).offset(page.offset).limit(page.limit).all()
            sql = text(f"select meitu_album.*, meitu_model.title as model_title from meitu_album left join meitu_model on meitu_album.model_name = meitu_model.name where meitu_album.title like '%' :s '%' and meitu_album.is_enabled = 1 limit :limit offset :offset")
            albums = session.execute(sql, {"s": s, "limit": page.limit, "offset": page.offset}).fetchall()

            sql = text(f"""select distinct meitu_model.* from meitu_model
                        join meitu_album on meitu_model.name = meitu_album.model_name
                        where meitu_album.title like '%' :s '%' limit 10
                    """)
            models = session.execute(sql, {"s": s}).fetchall()

            sql = text(f"""select distinct meitu_tag.* from meitu_tag
                        join meitu_album_tag on meitu_tag.id = meitu_album_tag.tag_id
                        join meitu_album on meitu_album_tag.album_id = meitu_album.id
                        where meitu_album.title like '%' :s '%' limit 20
                    """)
            tags = session.execute(sql, {"s": s}).fetchall()


            sql = text(f"""select distinct meitu_organize.* from meitu_organize
                        join meitu_album on meitu_organize.name = meitu_album.organize_name
                        where meitu_album.title like '%' :s '%' limit 10
                    """)
            organizes = session.execute(sql, {"s": s}).fetchall()
        else:
            albums = models = tags = organizes = []

    data = {
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "keyword": s,
        "albums": albums,
        "models": models,
        "tags": tags,
        "organizes": organizes
    }
    return templates.TemplateResponse("search-result.html", {"request": request, "data": data})
