import json

from draftsman.data import modules
from draftsman.data.modules import raw as modules

from building_resolver import BuildingResolver
from data_structures.recipe import Product
from materials import intermediate_products
from model_finalizer import ProductionLineProblem
from module import ModuleBuilder, Module
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import build_recipe_provider


def insert_module(recipe_provider, module: Module):
    moduleable_recipes = [
        recipe
        for recipe in recipe_provider.recipes
        if recipe.name in intermediate_products
    ]
    for recipe in moduleable_recipes:
        recipe.products = [product*(1+module.productivity) for product in recipe.products]
        recipe.energy = recipe.energy/(1+module.speed)
    return recipe_provider


def main():
    # deal with buildings
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(crafting_categories, overrides={"crafting": "assembling-machine-3"})
    # building_resolver = BuildingResolver(crafting_categories)
    # deal with recipes
    recipes_path = "data/recipes.json"
    recipe_provider = build_recipe_provider(recipes_path)
    module_builder = ModuleBuilder(modules)
    speed_module_2 = module_builder.build("speed-module-2")
    productivity_module_2 = module_builder.build("productivity-module-2")
    recipe_provider = insert_module(recipe_provider, speed_module_2*4+productivity_module_2*4)
    model_finalizer=ProductionLineProblem([("electronic-circuit", 15.0)])
    production_line_builder = ProductionLineBuilder(recipe_provider, building_resolver, model_finalizer)
    line = production_line_builder.build()
    line.print()
    return line


if __name__ == "__main__":
    main()
