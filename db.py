from peewee import *

db = SqliteDatabase('mydb.db3')

class Phrase(Model):
    text = TextField(unique=True)
    answer = TextField()

    class Meta:
        database = db
        indexes = ['text']
        order_by = ['text']

class Settings(Model):
    name = TextField(unique=True)
    value = TextField()

    class Meta:
        database = db
        indexes = ['name']
        order_by = ['name']


def get_data_from_db(model, col_search_name, search_value, col_value_name):
  try:
    element = model.select().where(getattr(model, col_search_name) == search_value).get()
    return getattr(element, col_value_name)
  except:
    return None

def get_setting_value(set_name, split_sign=None):
    result = get_data_from_db(Settings, 'name', set_name, 'value')
    if isinstance(split_sign, str):
        result = result.split(split_sign)
    return result

Phrase.create_table()
Settings.create_table()