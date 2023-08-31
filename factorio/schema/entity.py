from __future__ import annotations

from typing import Optional, List

import numpy as np
import pandas as pd
from pydantic import BaseModel, Extra

from factorio.curved_rail import curve_map
from factorio.schema.misc import RequestFilter, InfinitySettings, Connections, ControlBehavior, DropPosition, \
    PickupPosition
from factorio.schema.position import Position
from factorio.schema.tile import Tile


class Entity(BaseModel):

    class Config:
        extra = Extra.allow
    entity_number: int
    name: str
    position: Position
    bar: Optional[int] = None
    direction: Optional[int] = 8
    recipe: Optional[str] = None
    request_filters: Optional[List[RequestFilter]] = None
    neighbours: Optional[List[int]] = None
    buffer_size: Optional[float] = None
    type: Optional[str] = None
    infinity_settings: Optional[InfinitySettings] = None
    connections: Optional[Connections] = None
    control_behavior: Optional[ControlBehavior] = None
    override_stack_size: Optional[int] = None
    drop_position: Optional[DropPosition] = None
    pickup_position: Optional[PickupPosition] = None
    @property
    def size(self)->Position:
        buildings_raw=pd.read_csv('dimensions.csv',index_col='name')
        buildings={ name:Position(**kwargs)for name,kwargs in buildings_raw.T.to_dict().items()}
        pipes={ f'se-space-pipe-long-j-{size}': Position(x=1, y=size) for size in (3,5,7,9,15)}
        lookup={**buildings,**pipes}
        dimensions=lookup.get(self.name)
        if not dimensions:
            x,y = input(f"Dimensions for {self.name}?").split()
            to_write=buildings_raw.T
            to_write[self.name]=[x,y]
            to_write.T.to_csv('dimensions.csv')
            return self.size
        if 'pipe' in self.name:
            rotated = Position(x=dimensions.y, y=dimensions.x) if self.direction == 2 else dimensions
        else:
            rotated= Position(x=dimensions.y,y=dimensions.x) if self.direction%2==0 else dimensions
        return rotated
    @property
    def area(self):
        if self.name=='curved-rail':
            map=curve_map[self.direction]
            tiles=np.ndenumerate(map)
            return (self.position+Position(x=x-4,y=y-4)for (x,y),l in tiles if l == 1)
        if 'casting' in self.name or 'oiler' in self.name or 'turbine' in self.name or 'engine' in self.name or 'exchanger' in self.name or 'generator' in self.name:
            if self.direction in (2, 6):
                positions = [Position(x=x, y=y) for x, y in [(0, -1),(0,1),(1,1),(1,-1),(1,0)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x - 1, y=position.y - 1) for position in p]
            else:
                positions = [Position(x=y, y=x) for x, y in [(0, -1), (0, 1), (1, 1), (1, -1), (1, 0)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x - 1, y=position.y - 1) for position in p]
        if 'splitter' in self.name:
            if self.direction in (2,6):
                positions = [Position(x=x, y=y) for x, y in [(0,1)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x , y=position.y - 1) for position in p]
            else:
                positions = [Position(x=x, y=y) for x, y in [(1,0)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x - 1, y=position.y - 1) for position in p]
        if 'combinator' in self.name or 'pump' in self.name:
            if self.direction  not in (2, 6):
                positions = [Position(x=x, y=y) for x, y in [(0, 1)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x - 1, y=position.y - 1) for position in p]
            else:
                positions = [Position(x=x, y=y) for x, y in [(1, 0)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x - 1, y=position.y - 1) for position in p]
        if self.name=='straight-rail':
            if self.direction ==3:
                positions = [Position(x=x, y=y) for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                return [self.position + position for position in positions] + [self.position]
            elif self.direction == 7:
                positions = [Position(x=x, y=y) for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x - 1, y=position.y - 1) for position in p]
            elif self.direction == 5:
                positions = [Position(x=x, y=y) for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                p = [self.position + position for position in positions] + [self.position]
                return [Position(x=position.x - 1, y=position.y) for position in p]
            elif self.direction%2:
                positions = [Position(x=x,y=y) for x,y in [(-1,0),(1,0),(0,-1),(0,1)]]
                p=[self.position + position for position in positions]+[self.position]
                return [Position(x=position.x,y=position.y-1)for position in p]
            else:
                pass

        upper_left_corner=self.position+Position(x=-self.size.x/2,y=-self.size.y/2)
        return (upper_left_corner+Position(x=x,y=y)for x in range(int(self.size.x)) for y in range(int(self.size.y)))
    def foundations(self,name):
        return [Tile(position=position,name=name) for position in self.area]
    @property
    def scaffolding(self):
        return self.foundations('se-space-platform-scaffold')
    @property
    def landfill(self):
        return self.foundations('landfill')
