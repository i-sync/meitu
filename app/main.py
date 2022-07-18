#!/usr/bin/python
# -*- coding: utf-8 -*-

import json, time, random
import requests
from base64 import b64decode
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException

from starlette.responses import Response, RedirectResponse
from sqlalchemy import func, desc
from sqlalchemy.sql import text


from user_agents import parse

from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
#from slowapi import _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.library.models import session_scope, MeituAlbum, MeituMedia, MeituAlbumTag, MeituCategory, MeituContent, MeituImage, MeituModel, MeituOrganize, MeituTag
from app.routers import login, logs, beauty, handsome, news, street, model, tags, organize, search
from app.routers.login import manager
# from app.routers.beauty import beauty
from app.library.tools import date_filter, datetime_filter
from app.library.page import Page, PageAll, get_page_index
from app.library.logger import logger
from app.library.config import configs

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


@app.middleware("http")
async def add_user_agent_parse(request: Request, call_next):
    """
    fastapi middleware for user_agent parse
    reference: https://stackoverflow.com/questions/64602770/how-can-i-set-attribute-to-request-object-in-fastapi-from-middleware
    """
    if not request.url.path.startswith('/static') and request.headers.get("user-agent"):
        user_agent = parse(request.headers.get("user-agent"))
        request.state.user_agent = user_agent
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

# def get_category():
#     with session_scope() as session:
#         categories = session.query(XiurenCategory).filter(XiurenCategory.is_enabled == 1).all()
#         session.expunge_all()
#     # print(categories)
#     return categories

# def parse_user_agent(request: Request):
#     user_agent = parse(request.headers.get("user-agent"))
#     request.user_agent = user_agent

# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request, page = "1", order = "new"):
#     parse_user_agent(request)
#     categories = get_category()
#     page_index = get_page_index(page)
#     with session_scope() as session:
#         #rows = session.query(func.count(XiurenAlbum.id)).filter(XiurenAlbum.is_enabled == 1).scalar()
#         page = Page(200, page_index)
#         albums = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(func.random()).offset(page.offset).limit(page.limit).all()
#         for album in albums:
#             album.category = next(x for x in categories if x.id == album.category_id)
#         tops = session.query(XiurenAlbum).filter(XiurenAlbum.is_enabled == 1).order_by(desc(XiurenAlbum.view_count)).limit(10).all()
#         for album in tops:
#             album.category = next(x for x in categories if x.id == album.category_id)
#     data = {
#         "menu": MENU,
#         "page": page,
#         "categories": get_category(),
#         "tops": tops,
#         "albums": albums,
#         "url": request.url,
#         "meta": configs.meta,
#         "cover": tops[0].cover if len(tops) else f"{configs.meta.site_url}/static/images/cover.jpg",
#         "friendly_link": configs.friendly_link,
#         "keywords": configs.meta.keywords,
#         "description": configs.meta.description
#     }
#     return templates.TemplateResponse("index.html", {"request": request, "data": data})


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

