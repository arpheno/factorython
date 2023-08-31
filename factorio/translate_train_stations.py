import json

import clipboard

from factorio.factorio_loader import load_factorio
from factorio.schema.blueprint import Blueprint
from factorio.schema.book_model import BookModel
from factorio.schema.factorio_model import exclude_optional_json
from factorio.schema.model import Model

text = clipboard.paste()
book_model = BookModel(**json.loads(load_factorio(text)))
base = book_model.blueprint_book.blueprints[0]
book_model.blueprint_book.blueprints=[]
for i,x in enumerate(["Coal","Iron","Copper","Stone","Uranium"]):

    blueprint_json = exclude_optional_json(base).replace('field_1', "1").replace("Coal",x)
    new=Model(**json.loads(blueprint_json))
    new.index=i
    book_model.blueprint_book.blueprints.append(new)

clipboard.copy(book_model.to_factorio())
