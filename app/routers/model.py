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
from app.library.models import MeituMediaModel
from app.library.page import Page, PageAll, get_page_index
from app.library.config import toDict, configs



router = APIRouter()

@router.get('/model', response_class=HTMLResponse)
async def model(request: Request, page = "1"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituModel.id)).filter(MeituModel.is_enabled == 1).scalar()
        page = Page(rows, page_index)

        sql = f"""select meitu_model.*, count(1) as model_count from meitu_model
                    left join meitu_album on meitu_model.name = meitu_album.model_name
                    group by meitu_model.id
                    order by model_count desc limit {page.limit} offset {page.offset}"""
        models = session.execute(sql).fetchall()

    data ={
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "models": models
    }
    return templates.TemplateResponse("model.html", {"request": request, "data": data})

@router.get('/model/{name}', response_class=HTMLResponse)
async def model_detail(request: Request, name, page="1"):
    if not name:
        return RedirectResponse("/model")

    page_index = get_page_index(page)
    with session_scope() as session:
        model = session.query(MeituModel).filter(MeituModel.name == name, MeituModel.is_enabled == 1).first()

        if not model:
            return RedirectResponse("/404")

        summary = eval(model.summary)
        model.meta_keywords = ",".join([f"{x}:{summary[x]}" for x in summary.keys()])
        model.summary_info = "".join([f"<span class='px-1'>{x} : {summary[x]}</span>" for x in summary.keys()])

        rows = session.query(func.count(MeituAlbum.id)).filter(MeituAlbum.model_name == model.name, MeituAlbum.is_enabled == 1).scalar()
        page = Page(rows, page_index)
        #media.models = session.query(MeituMediaModel).filter(MeituMediaModel.media_id == media.id).all()
        albums = session.query(MeituAlbum).filter(MeituAlbum.model_name == model.name, MeituAlbum.is_enabled == 1).limit(page.limit).offset(page.offset).all()

    data = {
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "model": model,
        "albums": albums
    }

    return templates.TemplateResponse("model-detail.html", {"request": request, "data": data})