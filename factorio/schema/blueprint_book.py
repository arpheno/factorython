from typing import List

from pydantic import BaseModel, Extra

from factorio.schema.model import Model


class BlueprintBook(BaseModel):
    blueprints:List[Model]
    class Config:
        extra = Extra.allow
