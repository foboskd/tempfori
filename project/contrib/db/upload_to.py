import os
import hashlib
import datetime
import random


def upload_to(instance, filename):
    filename = filename.lower()
    hd = hashlib.sha256((str(datetime.datetime.now()) + str(random.random())).encode()).hexdigest()
    return os.path.join(str(instance.UPLOAD_TO), hd[:2], hd[2:4], '%s%s' % (hd, os.path.splitext(filename)[1]))


def upload_to_immutable(instance, filename):
    filename = filename.lower()
    hd = hashlib.sha256(filename.encode()).hexdigest()
    return os.path.join(str(instance.UPLOAD_TO), hd[:2], hd[2:4], '%s%s' % (hd, os.path.splitext(filename)[1]))
