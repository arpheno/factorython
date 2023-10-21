from typing import Dict

from draftsman.data.modules import raw

from building_resolver import BuildingResolver
from materials import intermediate_products
from module import Module, ModuleBuilder
from recipe_provider import RecipeProvider


class PrimitiveModuleInserter:
    def __init__(self, modules: Dict[str, Module]):
        self.modules = modules

    def __call__(self, recipe_provider) -> RecipeProvider:
        for recipe in recipe_provider.recipes:
            if 'ltn' in recipe.name:
                continue
            if recipe.name in intermediate_products:
                self.modules['productivity'](recipe)
            else:
                self.modules['speed'](recipe)

        return recipe_provider


def insert_module(recipe_provider, modules: Dict[str, Module]):
    for recipe in recipe_provider.recipes:
        if 'ltn' in recipe.name:
            continue
        if recipe.name in intermediate_products:
            modules['productivity'](recipe)
        else:
            modules['speed'](recipe)

    return recipe_provider

class BuildingSpecificModuleInserter:
    def __init__(self, modules: Dict[str, str], building_resolver: BuildingResolver, beacon_type: str = ''):
        module_builder = ModuleBuilder(raw)
        self.modules = {k: module_builder.build(name) for k, name in modules.items()}
        self.building_resolver = building_resolver
        self.beacon_power = {'': 0, 'small': 4, 'wab': 10}[beacon_type]

    def __call__(self, recipe_provider) -> RecipeProvider:
        for recipe in recipe_provider.recipes:
            if 'ltn' in recipe.name:
                continue
            building = self.building_resolver(recipe)
            module_slots =  building.module_specification.module_slots  if building.module_specification else 0
            if recipe.name in intermediate_products:
                print(f'putting {module_slots} modules in {building.name} for {recipe.name}')
                module = self.modules['productivity'] * module_slots+ \
                         self.modules['speed'] * self.beacon_power
            else:
                module = self.modules['speed'] * module_slots+ \
                         self.modules['speed'] * self.beacon_power

            module(recipe)
        return recipe_provider
