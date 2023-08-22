import json
import os
import time

from app.common import COLORS, MENU, templates
from app.library.config import configs, toDict
from app.library.models import (MeituAlbum, MeituCategory, MeituContent,
                                MeituImage, MeituMedia, MeituMediaModel,
                                MeituMediaTag, MeituModel, MeituOrganize,
                                MeituTag, session_scope)
from app.library.page import Page, PageAll, get_page_index
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func
from sqlalchemy.sql import text
from starlette.responses import RedirectResponse, Response

# from sqlalchemy.engine.row import Row





router = APIRouter()

@router.get('/model', response_class=HTMLResponse)
async def model(request: Request, page = "1"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituModel.id)).filter(MeituModel.is_enabled == 1).scalar()
        page = Page(rows, page_index)

        sql = text(f"""select meitu_model.*, count(meitu_album.id) as model_count from meitu_model
                    left join meitu_album on meitu_model.name = meitu_album.model_name
                    group by meitu_model.id
                    order by model_count desc limit {page.limit} offset {page.offset}""")
        models = session.execute(sql).fetchall()

        '''
        sql = text(f"""select count(1) as num from (select meitu_model.id, count(meitu_album.id) as model_count from meitu_model
                    left join meitu_album on meitu_model.name = meitu_album.model_name
                    group by meitu_model.id
                    having model_count > 0) as tmp""")
        rows = session.execute(sql).fetchone()
        page = Page(rows["num"], page_index)

        sql = text(f"""select meitu_model.*, count(meitu_album.id) as model_count from meitu_model
                    left join meitu_album on meitu_model.name = meitu_album.model_name
                    group by meitu_model.id
                    having model_count > 0
                    order by model_count desc limit {page.limit} offset {page.offset}""")
        '''

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
