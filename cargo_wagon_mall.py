import json
from math import ceil, floor
from pprint import pprint

from draftsman.data import modules
from draftsman.data.modules import raw as modules

from building_resolver import BuildingResolver
from cargo_wagon_block_maker.assembling_machines import (
    BlueprintMaker,
    AssemblingMachines,
)
from cargo_wagon_block_maker.beacons import Beacons
from cargo_wagon_assignment_problem import create_cargo_wagon_assignment_problem
from cargo_wagon_block_maker.connectors import Connectors
from cargo_wagon_block_maker.input_infrastructure import InputInfrastructure
from cargo_wagon_block_maker.output_infrastructure import OutputInfrastructure
from cargo_wagon_block_maker.power import Substations
from cargo_wagon_block_maker.train_head import TrainHead
from cargo_wagon_block_maker.wagons import Wagons
from materials import minable_resources, basic_processing
from model_finalizer import CargoWagonProblem, CargoWagonMallProblem
from module import ModuleBuilder, Module
from module_inserter import PrimitiveModuleInserter, BuildingSpecificModuleInserter
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import (
    build_recipe_provider,
    FreeRecipesAdder,
    RecipesRemover,
    apply_transformations,
)

assembly_path = "data/assembly_machine.json"
recipes_path = "data/recipes.json"


def cargo_wagon_mall():
    config = {
        'building_resolver_overrides':
            {
                "crafting": "assembling-machine-3",
                "basic-crafting": "assembling-machine-3",
                "crafting-with-fluid": "assembling-machine-3",
                "advanced-crafting": "assembling-machine-3",
                "chemistry": "chemical-plant",
                "pulverising": "assembling-machine-3"
            },
        'target_products': [(2, 'rail'), (1, 'cargo-wagon'), (4, 'stack-filter-inserter'), (4, 'assembling-machine-2')],
        'max_assemblers':32,
        'assembling_machine_modules':[
            "productivity-module-2","productivity-module-2","productivity-module-2","productivity-module-2",
        ]

    }
    target_products =config['target_products']
    max_assemblers = config['max_assemblers']
    # deal with buildings
    assembling_machine_modules = config['assembling_machine_modules']
    building_resolver_overrides=config['building_resolver_overrides']

    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories,
        overrides=building_resolver_overrides,
    )

    recipe_provider = build_recipe_provider(recipes_path)
    for _, target_product in target_products:
        recipe_provider.by_name(target_product)

    recipe_transformations = [
        FreeRecipesAdder(minable_resources),
        FreeRecipesAdder(basic_processing),
        BuildingSpecificModuleInserter(
            {"productivity": "productivity-module-2", "speed": "speed-module-2"},
            building_resolver,
            beacon_type="small",
        ),
    ]
    recipe_provider = apply_transformations(recipe_provider, recipe_transformations)
    blueprint_maker_modules = {
        "assembling_machines": AssemblingMachines(
            modules=assembling_machine_modules,
            building_resolver=building_resolver,
            recipe_provider=recipe_provider,
        ),
        "connectors": Connectors(),
        "wagons": Wagons(),
        "input_infrastructure": InputInfrastructure(),
        "power": Substations(),
        "output_infrastructure": OutputInfrastructure(),
        "beacons": Beacons(),
        "train_head": TrainHead(),
        # "roboports": Roboports(),
        # "lights": Lights(),
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    model_finalizer = CargoWagonMallProblem(target_products, max_assemblers=max_assemblers)

    # Determine the flow of goods through the production line
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
            rate = (
                    building_resolver(production_site.recipe).crafting_speed
                    / production_site.recipe.energy
            )
            products = {
                product.name: product.average_amount
                for product in production_site.recipe.products
            }
            ingredients = {
                ingredient.name: -ingredient.amount
                for ingredient in production_site.recipe.ingredients
            }
            for _ in range(floor(production_site.quantity)):
                production_sites.append(production_site.recipe.name)
                entity = {
                    good: products.get(good, 0) * rate + ingredients.get(good, 0) * rate
                    for good in products.keys() | ingredients.keys()
                }
                entities.append(entity)
            if not ceil(production_site.quantity) == floor(production_site.quantity):
                production_sites.append(production_site.recipe.name)
                entity = {
                    good: (products.get(good, 0) * rate + ingredients.get(good, 0) * rate) * (
                            production_site.quantity - floor(production_site.quantity))
                    for good in products.keys() | ingredients.keys()
                }
                entities.append(entity)

        else:
            global_input[
                production_site.recipe.products[0].name
            ] = production_site.quantity
    pprint(production_sites)
    ugly_reassignment = {}
    for site, entity in zip(production_sites, entities):
        ugly_reassignment[site] = entity
    # Now that we know the flow of goods, we can assign them to wagons by determining the order of machines
    production_sites, flows = create_cargo_wagon_assignment_problem(
        entities, global_input, production_sites, outputs=[product for factor, product in target_products]
    )
    blueprint_maker.make_blueprint(
        production_sites,
        ugly_reassignment=ugly_reassignment,
        output=[product for factor, product in target_products],
        flows=flows,
    )
    return line


if __name__ == "__main__":
    cargo_wagon_mall()
