

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.library.tools import date_filter, datetime_filter


templates = Jinja2Templates(directory="templates/enoma")
# add custom filter
templates.env.filters["datetime"] = datetime_filter
templates.env.filters["date"] = date_filter


MENU = {
    '/': '首页',
    '/beauty': '美女图片',
    '/handsome': '明星帅哥',
    '/news': '娱报',
    '/street': '街拍',
    '/tags': '主题合集',
    '/model': '模特库',
    '/organize': '写真机构',
}

COLORS = [
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info"
]