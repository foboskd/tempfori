import re
import datetime
from random import randrange
from datetime import timedelta
from dateutil.parser import parse


def date_parse(d: str) -> datetime.datetime:
    if re.match(r'\d\d\.\d\d\.\d\d\d\d', d):
        return datetime.datetime(*map(int, reversed(d.split('.'))))
    return parse(d)


def random_date(start: datetime.datetime, end: datetime.datetime) -> datetime.datetime:
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
