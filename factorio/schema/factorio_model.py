from __future__ import annotations

import base64
import json
import zlib

from pydantic import BaseModel, Extra
from pydantic.json import pydantic_encoder


class FactorioModel(BaseModel):
    class Config:
        extra = Extra.allow


    def to_factorio(self):
        blueprint_json = exclude_optional_json(self).replace('field_1', "1")
        with open('debug.json', 'w') as f:
            f.write(blueprint_json)
        factorio_blueprint = '0' + base64.b64encode(zlib.compress(blueprint_json.encode('utf-8'))).decode('utf-8')
        return factorio_blueprint


def union(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            union(value, node)
        else:
            destination[key] = value

    return destination


def exclude_optional_dict(model: BaseModel):
    return union(model.dict(exclude_unset=True), model.dict(exclude_none=True))


def exclude_optional_json(model: BaseModel):
    return json.dumps(exclude_optional_dict(model), default=pydantic_encoder)
