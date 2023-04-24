from peewee import Model
from typing import List
from models.product import Users, Groups
from models.utils import db

def connection(function: callable):
    def wrapper(*args, **kwargs):
        with db.connection():
            res = function(*args, **kwargs)
            db.commit()
            return res
    return wrapper


@connection
def create_table(*models: Model):
    for model in models:
        if not model.table_exists():
            model.create_table()


@connection
def get_user(user_id: str) -> List[Users]:
    return list(Users.select().filter(user_id=user_id))


@connection
def get_group(group_id: str) -> List[Groups]:
    return list(Groups.select().filter(group_id=group_id))


@connection
def get_all_groups(user_id: str) -> List[Groups]:
    return list(Groups.select().filter(user_id=user_id))


@connection
def create_user(user_id: str, user_name: str):
    Users.create(user_id=user_id, user_name=user_name)


@connection
def add_group(user_id: str, group_id: str, group_name: str):
    Groups.create(user_id=user_id, group_id=group_id, group_name=group_name)


if __name__ == '__main__':
    create_table(Users)
    create_table(Groups)
