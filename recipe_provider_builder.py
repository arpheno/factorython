import json

from typing import List

from custom_recipes import probe_recipes, spm_recipes
from data_structures.recipe import Recipe, Product
from module_inserter import Transformer
from parsing.recipe_parser import parse_recipes
from recipe_provider import RecipeProvider


def build_recipe_provider(recipes, building_resolver):
    recipes = parse_recipes(recipes)
    recipes.extend(probe_recipes)
    recipes.extend(spm_recipes)
    recipe_provider = RecipeProvider(recipes=recipes)
    return recipe_provider



def apply_transformers(recipe_provider: RecipeProvider,
                       transformations: List[Transformer]) -> RecipeProvider:
    for transformation in transformations:
        print(f'Applying transformation {transformation}')
        recipe_provider = transformation(recipe_provider)
    return recipe_provider


class FreeRecipesAdder(Transformer):
    def __init__(self, materials):
        self.materials = ([
            Recipe(
                name=f"ltn {name}",
                ingredients=[],
                products=[Product(name=name, amount=1, type="free")],
                energy=1,
                category="free",
            )
            for name in materials])

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        recipe_provider.recipes.extend(self.materials)
        return recipe_provider

    def __repr__(self):
        return f"FreeRecipesAdder({[f'{material.name}' for material in self.materials]})"


class RecipesRemover:
    def __init__(self, materials):
        self.materials = materials

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        recipe_provider.blocklist.extend(self.materials)
        return recipe_provider

    def __repr__(self):
        return f"RecipesRemover({[f'{material.name}' for material in self.materials]})"


class Barreler:
    def __init__(self, liquids):
        self.liquids = liquids

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        recipe_provider.blocklist.extend([f'ltn {liquid}' for liquid in self.liquids])

        recipe_provider.recipes.extend([
            Recipe(
                name=f"ltn {liquid}-barrel",
                ingredients=[],
                products=[Product(name=f'{liquid}-barrel', amount=1, type="free")],
                energy=1,
                category="free",
            )
            for liquid in self.liquids])
        return recipe_provider
