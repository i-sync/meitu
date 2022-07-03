import os, json, time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy import func, desc

from app.common import MENU, templates
from app.library.models import session_scope, MeituAlbum, MeituAlbumTag, MeituCategory, MeituContent, MeituImage, MeituModel, MeituOrganize, MeituTag
from app.library.page import Page, PageAll, get_page_index



router = APIRouter()

@router.get('/beauty', response_class=HTMLResponse)
async def beauty(request: Request, page = "1", order = "hot"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituAlbum.id)).filter(MeituAlbum.category_name == 'beauty', MeituAlbum.is_enabled == 1).scalar()
        page = Page(rows, page_index)
        albums = session.query(MeituAlbum).filter(MeituAlbum.category_name == 'beauty', MeituAlbum.is_enabled == 1).order_by(desc(MeituAlbum.origin_created_at if order == "new" else MeituAlbum.view_count)).offset(page.offset).limit(page.limit).all()

        for item in albums:
            if not item.model_name:
                continue
            model = session.query(MeituModel).filter(MeituModel.name == item.model_name, MeituModel.is_enabled == 1).first()
            if model:
                item.model_title =  model.title
        # tops = session.query(XiurenAlbum).filter(MeituAlbum.category_name == 'beauty', MeituAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.view_count)).limit(10).all()


    data ={
        "menu": MENU,
        "page": page,
        "albums": albums
    }
    return templates.TemplateResponse("beauty.html", {"request": request, "data": data})
