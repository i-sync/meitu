#!/usr/bin/python
# -*- coding: utf-8 -*-

from contextlib import contextmanager

from app.library.config import configs
from numpy import integer, tile
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text, Time, create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine(f"mysql+pymysql://{configs.database.user}:{configs.database.password}@{configs.database.host}:{configs.database.port}/{configs.database.database}", pool_recycle=3600)
DBSession = sessionmaker(bind=engine)
Base = declarative_base()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = DBSession()
    try:
        yield session
        #session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class MeituModel(Base):
    __tablename__ = "meitu_model"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    title = Column(String(500))
    summary = Column(String(500))
    description = Column(String(2048))
    cover = Column(String(200))
    cover_backup = Column(String(200))
    view_count = Column(Integer)
    created_at = Column(Float)
    is_enabled = Column(Boolean)


class MeituOrganize(Base):
    __tablename__ = "meitu_organize"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    title = Column(String(500))
    summary = Column(String(500))
    description = Column(String(2048))
    cover = Column(String(200))
    view_count = Column(Integer)
    created_at = Column(Float)
    is_enabled = Column(Boolean)


class MeituTag(Base):
    __tablename__ = "meitu_tag"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    title = Column(String(500))
    summary = Column(String(500))
    description = Column(String(2048))
    cover = Column(String(200))
    view_count = Column(Integer)
    created_at = Column(Float)
    is_enabled = Column(Boolean)

class MeituAlbum(Base):
    __tablename__ = "meitu_album"
    id = Column(Integer, primary_key=True)
    model_name = Column(String(100))
    organize_name = Column(String(100))
    category_name = Column(String(20))
    name = Column(String(200))
    title = Column(String(500))
    description = Column(String(2048))
    cover = Column(String(200))
    view_count = Column(Integer)
    origin_link = Column(String(500))
    origin_created_at = Column(Float)
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)

class MeituCategory(Base):
    __tablename__ = "meitu_category"
    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    title = Column(String(100))
    created_at = Column(Float)

class MeituImage(Base):
    __tablename__ = "meitu_image"
    id = Column(Integer, primary_key=True)
    album_id = Column(Integer)
    image_url = Column(String(200))
    backup_url = Column(String(200))
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)

class MeituAlbumTag(Base):
    __tablename__ = "meitu_album_tag"
    id = Column(Integer, primary_key=True)
    album_id = Column(Integer)
    tag_id = Column(Integer)
    created_at = Column(Float)

class MeituAlbumModel(Base):
    __tablename__ = "meitu_album_model"
    id = Column(Integer, primary_key=True)
    album_id = Column(Integer)
    model_id = Column(Integer)
    created_at = Column(Float)

class MeituMedia(Base):
    __tablename__ = "meitu_media"
    id = Column(Integer, primary_key=True)
    category_name = Column(String(20))
    keywords = Column(String(200))
    name = Column(String(200))
    title = Column(String(500))
    description = Column(String(2048))
    cover = Column(String(200))
    view_count = Column(Integer)
    origin_link = Column(String(500))
    origin_created_at = Column(Float)
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)

class MeituContent(Base):
    __tablename__ = "meitu_content"
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer)
    content = Column(Text)
    created_at = Column(Float)
    updated_at = Column(Float)
    is_enabled = Column(Boolean)

class MeituMediaTag(Base):
    __tablename__ = "meitu_media_tag"
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer)
    tag_id = Column(Integer)
    created_at = Column(Float)

class MeituMediaModel(Base):
    __tablename__ = "meitu_media_model"
    id = Column(Integer, primary_key=True)
    media_id = Column(Integer)
    model_id = Column(Integer)
    created_at = Column(Float)



class MeituTmpModel(Base):
    __tablename__ = "meitu_tmp_model"
    name = Column(String(100), primary_key=True)
    model_url = Column(String(200))


class MeituSearch(Base):
    __tablename__ = "meitu_search"
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    count = Column(Integer)
    created_at = Column(Float)
