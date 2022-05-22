from datetime import datetime
from typing import Optional, Union

import arrow


def now_datetime() -> datetime:
    return arrow.utcnow().datetime


def time_2_iso_format(val: Union[datetime, int]) -> str:
    return arrow.get(val).isoformat()


def shifted_datetime(
    dt: Optional[Union[datetime, arrow.Arrow]] = None,
    **kwargs,
) -> datetime:
    base = arrow.get(dt) if dt else arrow.utcnow()
    return base.shift(**kwargs).datetime
