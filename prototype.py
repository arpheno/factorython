from typing import Dict

from pydantic import BaseModel




class Prototype(BaseModel):
    name: str
    crafting_categories: Dict[str, bool]
    crafting_speed: float
    @property
    def crafting_categories_list(self):
        return list(self.crafting_categories.keys())
    def __str__(self):
        return self.name
    def __hash__(self):
        return hash(self.name)




