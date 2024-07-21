from dataclasses import dataclass
from math import floor

from numpy import ceil

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

    @property
    def import_export_dictionary_entities(self) -> [(str, dict)]:
        """
        Computes the entities based on the quantity of the production site.
        Each entity is a dictionary representing a summary of the recipe scaled by the production rate.

        :return: A list of dictionaries representing the entities.
        """

        rate = 1 / self.recipe.energy
        entities = [(self.recipe.name, self.recipe.summary() * rate)] * floor(self.quantity)
        fractional_modifier = (self.quantity - floor(self.quantity))
        fractional_entity = [] if ceil(self.quantity) == floor(self.quantity) else [
            (self.recipe.name, self.recipe.summary() * rate * fractional_modifier)]

        return entities + fractional_entity