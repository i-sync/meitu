import os, json, time
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from sqlalchemy import func, desc
from sqlalchemy.sql import text
# from sqlalchemy.engine.row import Row

from starlette.responses import Response, RedirectResponse

from app.common import MENU, COLORS, templates
from app.library.models import session_scope, MeituMedia, MeituMediaTag, MeituCategory, MeituContent, MeituImage, MeituModel, MeituOrganize, MeituTag
from app.library.models import MeituMediaModel
from app.library.page import Page, PageAll, get_page_index
from app.library.config import toDict, configs



router = APIRouter()

@router.get('/street', response_class=HTMLResponse)
async def street(request: Request, page = "1", order = "new"):
    page_index = get_page_index(page)

    with session_scope() as session:
        rows = session.query(func.count(MeituMedia.id)).filter(MeituMedia.category_name == 'street', MeituMedia.is_enabled == 1).scalar()
        page = Page(rows, page_index)

        order_by = "view_count" if order == "hot" else "origin_created_at"
        sql = f"select * from meitu_media where meitu_media.category_name = 'street' and meitu_media.is_enabled = 1 order by meitu_media.{order_by} desc limit {page.limit} offset {page.offset}"
        medias = session.execute(sql).fetchall()

        if request.state.user_agent.is_mobile:
            tops = session.query(MeituMedia).filter(MeituMedia.category_name == 'street', MeituMedia.is_enabled == 1).order_by(desc(MeituMedia.view_count)).limit(10).all()
        else:
            tops = []

    data ={
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "medias": medias,
        "tops": tops
    }
    return templates.TemplateResponse("street.html", {"request": request, "data": data})

@router.get('/street/{name}', response_class=HTMLResponse)
async def street_detail(request: Request, name, page="1"):
    if not name:
        return RedirectResponse("/street")

    page_index = get_page_index(page)
    with session_scope() as session:
        media = session.query(MeituMedia).filter(MeituMedia.category_name == 'street', MeituMedia.name == name, MeituMedia.is_enabled == 1).first()

        if not media:
            return RedirectResponse("/404")

        media.tags =[]
        sql = text("""select tag.* from meitu_tag tag
                    inner join meitu_media_tag r on tag.id = r.tag_id
                    where r.media_id = :media_id """)
        tags = session.execute(sql, {"media_id": media.id}).fetchall()
        for tag in tags:
            tag = toDict(tag._asdict())
            tag.color = COLORS[tag.id % len(COLORS)]
            media.tags.append(tag)

        #media.models = session.query(MeituMediaModel).filter(MeituMediaModel.media_id == media.id).all()
        media.models =[]
        sql = text("""select model.* from meitu_model model
                    inner join meitu_media_model r on model.id = r.model_id
                    where r.media_id = :media_id """)
        models = session.execute(sql, {"media_id": media.id}).fetchall()
        for model in models:
            model = toDict(model._asdict())
            media.models.append(model)


        media.meta_keywords = ','.join([x for x in eval(media.keywords) if x]) if media.keywords else ''

        rows = session.query(func.count(MeituContent.id)).filter(MeituContent.media_id == media.id, MeituContent.is_enabled == 1).scalar()
        page = PageAll(rows, page_index, page_size=1)
        media.contents = session.query(MeituContent).filter(MeituContent.media_id == media.id, MeituContent.is_enabled == 1).limit(page.limit).offset(page.offset).all()

        # related media
        if len(media.tags):
            # https://stackoverflow.com/questions/2142922/mysql-select-related-objects-by-tags
            sql = text("""SELECT media.id, media.name, media.title, media.cover, media.origin_created_at, media.view_count,  COUNT(1) AS tag_count
                FROM meitu_media_tag T1
                JOIN meitu_media_tag T2
                ON T1.tag_id = T2.tag_id AND T1.media_id != T2.media_id
                JOIN meitu_media media ON T2.media_id = media.id
                WHERE media.category_name = 'street' AND T1.media_id = :media_id
                GROUP BY T2.media_id
                ORDER BY tag_count DESC
                limit 20;""")
            media.related = session.execute(sql, {'media_id': media.id}).fetchall()
        else:
            media.related = session.query(MeituMedia).filter(MeituMedia.category_name == 'street', MeituMedia.is_enabled == 1).limit(20).all()

        if not request.state.user_agent.is_mobile:
            tops = session.query(MeituMedia).filter(MeituMedia.category_name == 'street', MeituMedia.id != media.id, MeituMedia.is_enabled == 1).order_by(desc(MeituMedia.view_count)).limit(10).all()
            latest = session.query(MeituMedia).filter(MeituMedia.category_name == 'street', MeituMedia.id != media.id, MeituMedia.is_enabled == 1).order_by(desc(MeituMedia.origin_created_at)).limit(10).all()
        else:
            tops = []
            latest = []
    data = {
        "menu": MENU,
        "meta": configs.meta,
        "page": page,
        "media": media,
        "tops": tops,
        "latest": latest
    }

    return templates.TemplateResponse("street-detail.html", {"request": request, "data": data})