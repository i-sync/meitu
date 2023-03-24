#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import random
import time
from base64 import b64decode
from typing import Optional

import requests
from cashews import cache
from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
#from slowapi import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from sqlalchemy import desc, func
from sqlalchemy.sql import text
from starlette.responses import RedirectResponse, Response
from user_agents import parse

from app.common import COLORS, MENU, templates
from app.library.config import configs
from app.library.logger import logger
from app.library.models import (MeituAlbum, MeituAlbumTag, MeituCategory,
                                MeituContent, MeituImage, MeituMedia,
                                MeituModel, MeituOrganize, MeituTag,
                                session_scope)
from app.library.page import Page, PageAll, get_page_index
# from app.routers.beauty import beauty
from app.library.tools import date_filter, datetime_filter
from app.routers import (beauty, handsome, login, logs, model, news, organize,
                         search, street, tags)
from app.routers.login import manager

app = FastAPI()
app.include_router(login.router)
app.include_router(logs.router)
app.include_router(beauty.router)
app.include_router(handsome.router)
app.include_router(news.router)
app.include_router(street.router)
app.include_router(model.router)
app.include_router(tags.router)
app.include_router(organize.router)
app.include_router(search.router)



app.mount("/static", StaticFiles(directory="static"), name="static")



def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Build a simple Redirect response that redirect the error details of the rate limit
    that was hit. If no limit is hit, the countdown is added to headers.
    """
    response = RedirectResponse(url="/limit-error")
    response = request.app.state.limiter._inject_headers(
        response, request.state.view_rate_limit
    )
    return response

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

manager.useRequest(app)

class NotAuthenticatedException(Exception):
    pass

# these two argument are mandatory
def exc_handler(request, exc):
    return RedirectResponse(url='/login')

# This will be deprecated in the future
# set your exception when initiating the instance
# manager = LoginManager(..., custom_exception=NotAuthenticatedException)
manager.not_authenticated_exception = NotAuthenticatedException
# You also have to add an exception handler to your app instance
app.add_exception_handler(NotAuthenticatedException, exc_handler)



async def make_cached_data(response: StreamingResponse):
    content = b""
    async for chunk in response.body_iterator:
        content += chunk

    if response.media_type == 'application/json':
        response_cls = ORJSONResponse
    else:
        response_cls = Response

    return response_cls(
        status_code=response.status_code,
        content=content,
        headers=response.headers,
        media_type=response.media_type,
        background=response.background,
    )


cache.setup("mem://?check_interval=10&size=10000")

@app.middleware("http")
async def cache_html_response(request: Request, call_next):
    """
    How to cache StreamReponse or make a cache middleware
    https://github.com/tiangolo/fastapi/issues/4751

    cache all GET request to 1h, except view_count, static files.
    """
    if request.scope['method'] == "GET" \
        and not request.url.path.startswith('/static') \
        and request.url.path.find('/plus/count') == -1 :

        key = f"{request.scope['method']}-{request.scope['path']}-{str(request.scope['query_string'])}-{request.state.user_agent.is_mobile if request.state.user_agent else 'None'}"
        cached_data = await cache.get(key)

        # missing cache
        if cached_data is None:
            response = await call_next(request)

            # only cache when status code == 200
            if response.status_code == 200:
                # 写入缓存
                response = await make_cached_data(response)
                await cache.set(key, response, expire= 60 * 60 * 24)

            return response

        return cached_data

    return await call_next(request)


@app.middleware("http")
async def add_user_agent_parse(request: Request, call_next):
    """
    fastapi middleware for user_agent parse
    reference: https://stackoverflow.com/questions/64602770/how-can-i-set-attribute-to-request-object-in-fastapi-from-middleware
    """
    if not request.url.path.startswith('/static') and request.headers.get("user-agent"):
        try:
            user_agent = parse(request.headers.get("user-agent"))
            request.state.user_agent = user_agent
        except:
            pass
    return await call_next(request)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    fastapi middleware add process time for response header
    reference: https://fastapi.tiangolo.com/tutorial/middleware/
    """
    if not request.url.path.startswith('/static'):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    return await call_next(request)

# def check_login(request: Request):
#     user = request.state.user
#     if user is None:
#         raise NotAuthenticatedException()
#     else:
#         return user

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    with session_scope() as session:

        # models
        sql = f"""select meitu_model.*, count(meitu_album.id) as model_count from meitu_model
                    left join meitu_album on meitu_model.name = meitu_album.model_name
                    where meitu_model.is_enabled = 1 and meitu_model.cover is not null
                    group by meitu_model.id
                    order by model_count desc limit 12"""
        models = session.execute(sql).fetchall()

        # tags
        sql = f"""select meitu_tag.*, count(meitu_album_tag.id) as tag_count from meitu_tag
                    left join meitu_album_tag on meitu_tag.id = meitu_album_tag.tag_id
                    where meitu_tag.is_enabled = 1
                    group by meitu_tag.id
                    order by tag_count desc limit 18"""
        tags = session.execute(sql).fetchall()

        # organizes
        organizes = []
        # sql = f"""select meitu_organize.*, count(meitu_album.id) as organize_count from meitu_organize
        #             left join meitu_album on meitu_organize.name = meitu_album.organize_name
        #             where meitu_organize.is_enabled = 1
        #             group by meitu_organize.id
        #             order by organize_count desc limit 20"""
        # organizes = session.execute(sql).fetchall()

        # beauty
        sql = """select meitu_album.*, meitu_model.title as model_title
            from meitu_album
            left join meitu_model on meitu_album.model_name = meitu_model.name
            where meitu_album.category_name = 'beauty' and meitu_album.is_enabled = 1 order by meitu_album.view_count desc limit 12"""
        beauty = session.execute(sql).fetchall()

        # handsome
        sql = """select meitu_album.*, meitu_model.title as model_title
            from meitu_album
            left join meitu_model on meitu_album.model_name = meitu_model.name
            where meitu_album.category_name = 'handsome' and meitu_album.is_enabled = 1 order by meitu_album.view_count desc limit 12"""
        handsome = session.execute(sql).fetchall()

        # news
        news = session.query(MeituMedia).filter(MeituMedia.category_name == 'news', MeituMedia.is_enabled == 1).order_by(desc(MeituMedia.view_count)).limit(12).all()

        # street
        street = session.query(MeituMedia).filter(MeituMedia.category_name == 'street', MeituMedia.is_enabled == 1).order_by(desc(MeituMedia.view_count)).limit(12).all()

    data ={
        "menu": MENU,
        "meta": configs.meta,
        "models": models,
        "tags": tags,
        "organizes": organizes,
        "beauty": beauty,
        "handsome": handsome,
        "news": news,
        "street": street
    }
    return templates.TemplateResponse("index.html", {"request": request, "data": data})


# @app.get("/limit-error", response_class=HTMLResponse)
# async def limit_error(request: Request):
#     parse_user_agent(request)
#     categories = get_category()

#     data = {
#         "menu": MENU,
#         "message": "Rate limit exceeded",
#         "categories": categories,
#         "url": request.url,
#         "meta": configs.meta,
#         "friendly_link": configs.friendly_link,
#         "keywords": configs.meta.keywords
#     }
#     return templates.TemplateResponse("error.html", {"request": request, "data": data})

@app.get("/album/plus/count/{id}", response_class=HTMLResponse)
async def count(id, request: Request):
    if not id or not id.isdigit():
        return "document.write('0');"
    view_count = 0
    with session_scope() as session:
        album = session.query(MeituAlbum).filter(MeituAlbum.id == int(id), MeituAlbum.is_enabled == 1).first()
        if album:
            album.view_count += 1
            view_count = album.view_count
            session.commit()
    return f"document.write('{view_count}');"

@app.get("/media/plus/count/{id}", response_class=HTMLResponse)
async def count(id, request: Request):
    if not id or not id.isdigit():
        return "document.write('0');"
    view_count = 0
    with session_scope() as session:
        media = session.query(MeituMedia).filter(MeituMedia.id == int(id), MeituMedia.is_enabled == 1).first()
        if media:
            media.view_count += 1
            view_count = media.view_count
            session.commit()
    return f"document.write('{view_count}');"

@app.get("/model/plus/count/{id}", response_class=HTMLResponse)
async def count(id, request: Request):
    if not id or not id.isdigit():
        return "document.write('0');"
    with session_scope() as session:
        item = session.query(MeituModel).filter(MeituModel.id == int(id), MeituModel.is_enabled == 1).first()
        if item:
            item.view_count += 1
            session.commit()
    return ""

@app.get("/organize/plus/count/{id}", response_class=HTMLResponse)
async def count(id, request: Request):
    if not id or not id.isdigit():
        return "document.write('0');"
    with session_scope() as session:
        item = session.query(MeituOrganize).filter(MeituOrganize.id == int(id), MeituOrganize.is_enabled == 1).first()
        if item:
            item.view_count += 1
            session.commit()
    return ""

@app.get("/tags/plus/count/{id}", response_class=HTMLResponse)
async def count(id, request: Request):
    if not id or not id.isdigit():
        return "document.write('0');"
    with session_scope() as session:
        item = session.query(MeituTag).filter(MeituTag.id == int(id), MeituTag.is_enabled == 1).first()
        if item:
            item.view_count += 1
            session.commit()
    return ""
