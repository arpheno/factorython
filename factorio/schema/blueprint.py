from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, Extra

from factorio.schema.misc import Icon
from factorio.schema.tile import Tile
from factorio.schema.entity import Entity


class Blueprint(BaseModel):
    icons: List[Icon]
    entities: List[Entity]
    tiles: Optional[List[Tile]]=Field(default_factory=list)
    item: str
    version: int
    def scaffold(self):
        for entity in self.entities:
            self.tiles.extend(entity.scaffolding)
        self.tiles = list(set(self.tiles))
    def landfill(self):
        for entity in self.entities:
            self.tiles.extend(entity.landfill)
        self.tiles = list(set(self.tiles))
    class Config:
        extra = Extra.allow
