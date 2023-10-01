import json

from custom_recipes import probe_recipes
from materials import se_materials, nauvis_materials, minable_resources, basic_processing
from parsing.recipe_parser import parse_recipes
from recipe_provider import RecipeProvider


def build_recipe_provider(recipes_path):
    with open(recipes_path, "r") as f:
        recipes = json.load(f)
    recipes = parse_recipes(recipes)
    recipes.extend(probe_recipes)
    ltn_materials = []
    ltn_materials.extend(se_materials)
    # ltn_materials.extend(nauvis_materials)
    ltn_materials.extend(minable_resources)
    ltn_materials.extend(basic_processing)
    recipe_provider = RecipeProvider(recipes=recipes, ltn_materials=ltn_materials)
    return recipe_provider
