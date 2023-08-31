from __future__ import annotations

from pydantic import Extra

from factorio.schema.blueprint_book import BlueprintBook
from factorio.schema.factorio_model import FactorioModel


class BookModel(FactorioModel):
    blueprint_book:BlueprintBook
    class Config:
        extra = Extra.allow
