import json

from custom_recipes import probe_recipes
from data_structures.recipe import Recipe, Product
from materials import se_materials, nauvis_materials, minable_resources, basic_processing
from parsing.recipe_parser import parse_recipes
from recipe_provider import RecipeProvider


def build_recipe_provider(recipes_path):
    with open(recipes_path, "r") as f:
        recipes = json.load(f)
    recipes = parse_recipes(recipes)
    recipes.extend(probe_recipes)
    recipe_provider = RecipeProvider(recipes=recipes)
    return recipe_provider


def apply_transformations(recipe_provider: RecipeProvider, transformations) -> RecipeProvider:
    for transformation in transformations:
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
