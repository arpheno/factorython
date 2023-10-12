from typing import Dict

from materials import intermediate_products
from module import Module
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
