import json
from math import ceil
from pprint import pprint
from random import shuffle

from draftsman.constants import Direction
from draftsman.data import modules
from draftsman.data.modules import raw as modules

from building_resolver import BuildingResolver
from cargo_wagon_block_maker.assembling_machines import (
    BlueprintMaker,
    assembling_machines,
)
from cargo_wagon_block_maker.cargo_wagon_blueprint import cargo_wagon_blueprint
from cargo_wagon_assignment_problem import create_cargo_wagon_assignment_problem
from cargo_wagon_block_maker.connectors import Connectors
from cargo_wagon_block_maker.input_infrastructure import InputInfrastructure
from cargo_wagon_block_maker.output_infrastructure import OutputInfrastructure
from cargo_wagon_block_maker.power import Power
from cargo_wagon_block_maker.wagons import Wagons
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
        crafting_categories,
        overrides={
            "crafting": "assembling-machine-3",
            "crafting-with-fluid": "assembling-machine-3",
        },
    )
    recipes_path = "data/recipes.json"

    recipe_provider = build_recipe_provider(
        recipes_path, ["electronic-circuit", "advanced-circuit"]
    )
    module_builder = ModuleBuilder(modules)
    recipe_provider = insert_module(
        recipe_provider,
        module_builder.build("speed-module-2") * 4
        + module_builder.build("productivity-module-2") * 4,
    )
    target_product = "rocket-control-unit"
    # model_finalizer = CargoWagonProblem([("advanced-circuit")], max_assemblers=24)
    model_finalizer = CargoWagonProblem([target_product], max_assemblers=32)
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
                rate=building_resolver(production_site.recipe).crafting_speed / production_site.recipe.energy
                products = {
                    product.name: product.average_amount
                    for product in production_site.recipe.products
                }
                ingredients = {
                    ingredient.name: -ingredient.amount
                    for ingredient in production_site.recipe.ingredients
                }
                entity = {
                    good: products.get(good, 0)*rate + ingredients.get(good, 0)*rate
                    for good in products.keys() | ingredients.keys()
                }
                entities.append(entity)
        else:
            global_input[production_site.recipe.products[0].name] = (
                production_site.quantity * 1.1
            )
    pprint(production_sites)
    ugly_reassignment = {}
    for site, entity in zip(production_sites, entities):
        ugly_reassignment[site] = entity
    production_sites = create_cargo_wagon_assignment_problem(
        entities, global_input, production_sites
    )
    cargo_wagon_blueprint(production_sites, ugly_reassignment, output=target_product)
    blueprint_maker_modules = {
        "assembling_machines": assembling_machines,
        "connectors": Connectors(),
        'wagons':Wagons(),
        'input_infrastructure': InputInfrastructure(),
        'power':Power(),
        'output_infrastructure':OutputInfrastructure(),
    }
    maker = BlueprintMaker(
        modules=blueprint_maker_modules,
        building_resolver=building_resolver,
        recipe_provider=recipe_provider,
    )
    maker.make_blueprint(
        production_sites, ugly_reassignment=ugly_reassignment, output=target_product
    )
    return line


if __name__ == "__main__":
    main()
