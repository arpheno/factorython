from __future__ import annotations

from pydantic import BaseModel, Extra

from factorio.schema.misc import Position1


class Tile(BaseModel):
    position: Position1
    name: str

    class Config:
        extra = Extra.forbid
    def __hash__(self):
        return hash((self.position.x,self.position.y,self.name))
