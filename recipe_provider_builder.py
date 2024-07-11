import json

from custom_recipes import probe_recipes, spm_recipes
from data_structures.recipe import Recipe, Product
from parsing.recipe_parser import parse_recipes
from recipe_provider import RecipeProvider


def build_recipe_provider(recipes,building_resolver):
    recipes = parse_recipes(recipes)
    recipes.extend(probe_recipes)
    recipes.extend(spm_recipes)
    recipe_provider = RecipeProvider(recipes=recipes,building_resolver=building_resolver)
    return recipe_provider


def apply_transformations(recipe_provider: RecipeProvider, transformations) -> RecipeProvider:
    for transformation in transformations:
        print(f'Applying transformation {transformation}')
        recipe_provider = transformation(recipe_provider)
    return recipe_provider


class FreeRecipesAdder:
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


class RecipesRemover:
    def __init__(self, materials):
        self.materials = materials

    def __call__(self, recipe_provider: RecipeProvider) -> RecipeProvider:
        recipe_provider.blocklist.extend(self.materials)
        return recipe_provider


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
