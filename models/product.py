from peewee import Model, PrimaryKeyField, IntegerField, CharField, BooleanField
from models.utils import db


class Users(Model):
    id = PrimaryKeyField()
    user_id = CharField()
    user_name = CharField()

    class Meta:
        database = db


class Groups(Model):
    id = PrimaryKeyField()
    user_id = CharField()
    group_id = CharField()
    group_name = CharField()

    class Meta:
        database = db
