from datetime import datetime
from typing import Union

import arrow


def now_datetime() -> datetime:
    return arrow.utcnow().datetime


def time_2_iso_format(val: Union[datetime, int]) -> str:
    return arrow.get(val).isoformat()
