from typing import Dict

from materials import intermediate_products
from module import Module


def insert_module(recipe_provider, modules:Dict[str,Module]):
    for recipe in recipe_provider.recipes:
        if recipe.name in intermediate_products:
            modules['productivity'](recipe)
        else:
            modules['speed'](recipe)

    return recipe_provider
