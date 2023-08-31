from __future__ import annotations

from pydantic import BaseModel, Extra


class Position(BaseModel):
    x: float
    y: float

    class Config:
        extra = Extra.forbid
    def __add__(self, other):
        return Position(x=self.x+other.x,y=self.y+other.y)
