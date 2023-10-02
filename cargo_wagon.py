import json
from math import ceil
from pprint import pprint
from random import shuffle

from draftsman.constants import Direction
from draftsman.data import modules
from draftsman.data.modules import raw as modules

from building_resolver import BuildingResolver
from cargo_block_maker import cargo_wagon_blueprint
from cargo_wagon_assignment_problem import create_cargo_wagon_assignment_problem
from model_finalizer import CargoWagonProblem
from module import ModuleBuilder
from module_inserter import insert_module
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import build_recipe_provider


def main():
    # deal with buildings
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories, overrides={"crafting": "assembling-machine-3"}
    )
    recipes_path = "data/recipes.json"
    recipe_provider = build_recipe_provider(recipes_path)
    module_builder = ModuleBuilder(modules)
    recipe_provider = insert_module(
        recipe_provider,
        module_builder.build("speed-module-2") * 4
        + module_builder.build("productivity-module-2") * 4,
    )

    model_finalizer = CargoWagonProblem([("advanced-circuit")], max_assemblers=32)
    # model_finalizer = CargoWagonProblem([("electric-engine-unit")], max_assemblers=32)
    # model_finalizer = CargoWagonProblem([("electronic-circuit")], max_assemblers=8)
    production_line_builder = ProductionLineBuilder(
        recipe_provider, building_resolver, model_finalizer
    )
    line = production_line_builder.build()
    line.print()
    production_sites = []
    global_input = {}
    entities = []
    for production_site in line.production_sites.values():
        if not "ltn" in production_site.recipe.name:
            for q in range(ceil(production_site.quantity)):
                production_sites.append(production_site.recipe.name)
                products = {
                    product.name: product.average_amount
                    for product in production_site.recipe.products
                }
                ingredients = {
                    ingredient.name: -ingredient.amount
                    for ingredient in production_site.recipe.ingredients
                }
                entity = {
                    good: products.get(good, 0) + ingredients.get(good, 0)
                    for good in products.keys() | ingredients.keys()
                }
                entities.append(entity)
        else:
            global_input[production_site.recipe.products[0].name] = (
                production_site.quantity * 1.1
            )
    pprint(production_sites)
    production_sites = create_cargo_wagon_assignment_problem(
        entities, global_input, production_sites
    )
    cargo_wagon_blueprint(production_sites)
    return line


if __name__ == "__main__":
    main()
