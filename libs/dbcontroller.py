#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from libs.common import config

from peewee import *
from playhouse.postgres_ext import *


db = config()['db']

database = PostgresqlExtDatabase(
    db['name'],
    user=db['user'],
    password=db['password'],
    host=db['hostname'],
    port=db['port']
)


class BaseModel(Model):
    class Meta:
        database = database

