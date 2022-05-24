import json
from datetime import datetime

from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from comment.config import settings
from comment.utils.time import time_2_iso_format

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=10,  # sa defaults to 5
    pool_recycle=1800,  # mysql defaults to 8 hours, cdb `wait_timeout = 3600`
    max_overflow=-1,  # allow connection spikes
    echo=settings.SQLALCHEMY_ECHO,  # logger level
    echo_pool=settings.SQLALCHEMY_ECHO,
    isolation_level='READ COMMITTED',
    json_serializer=lambda obj: json.dumps(
        jsonable_encoder(
            obj, custom_encoder={datetime: lambda val: time_2_iso_format(val)}
        )
    ),
)

Session = sessionmaker(bind=engine, autocommit=False)


def get_db():
    """Database dependency"""
    db = Session()
    try:
        yield db
    finally:
        db.close()
