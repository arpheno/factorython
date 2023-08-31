from dataclasses import dataclass

from data_structures.assembling_machine import AssemblingMachine
from data_structures.recipe import Recipe


@dataclass
class ProductionSite:
    recipe: Recipe
    quantity: float
    building: AssemblingMachine

    @property
    def flow(self):
        rate_per_building = self.building.crafting_speed / self.recipe.energy
        return rate_per_building * self.quantity

    @property
    def building_count(self):
        return int(self.quantity) if self.quantity == int(self.quantity) else int(self.quantity) + 1
