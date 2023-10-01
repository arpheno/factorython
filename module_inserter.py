from materials import intermediate_products
from module import Module


def insert_module(recipe_provider, module: Module):
    moduleable_recipes = [
        recipe
        for recipe in recipe_provider.recipes
        if recipe.name in intermediate_products
    ]
    for recipe in moduleable_recipes:
        recipe.products = [
            product * (1 + module.productivity) for product in recipe.products
        ]
        recipe.energy = recipe.energy / (1 + module.speed)
    return recipe_provider
