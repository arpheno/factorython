import json
from functools import partial
from itertools import chain
from pprint import pprint

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
from model_finalizer import  CargoWagonMallProblem
from module_inserter import  BuildingSpecificModuleInserter
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import (
    build_recipe_provider,
    FreeRecipesAdder,
    apply_transformations,
)

import yaml


def load_config(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def build_building_resolver(assembly, building_resolver_overrides):
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories,
        overrides=building_resolver_overrides,
    )
    return building_resolver


def cargo_wagon_mall(config):
    target_products = config["target_products"]
    max_assemblers = config["max_assemblers"]
    # deal with buildings
    assembling_machine_modules = config["assembling_machine_modules"]
    building_resolver_overrides = config["building_resolver_overrides"]
    assembly_loader = partial(
        lambda path: json.load(open(path)), config["assembly_path"]
    )
    recipe_loader = partial(lambda path: json.load(open(path)), config["recipe_path"])

    assembly = assembly_loader()
    recipes = recipe_loader()

    recipe_provider = build_recipe_provider(recipes)
    building_resolver = build_building_resolver(assembly, building_resolver_overrides)
    try:
        for _, target_product in target_products:
            recipe_provider.by_name(target_product)
    except ValueError:
        raise ValueError(f"Recipe {target_product} not found")

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
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    model_finalizer = CargoWagonMallProblem(
        target_products, max_assemblers=max_assemblers
    )

    # Determine the flow of goods through the production line
    production_line_builder = ProductionLineBuilder(
        recipe_provider, building_resolver, model_finalizer
    )
    line = production_line_builder.build()
    line.print()

    global_input = {
        production_site.recipe.products[0].name: production_site.quantity
        for production_site in line.production_sites.values()
        if "ltn" in production_site.recipe.name
    }

    temp = chain(
        *[
            production_site.entities
            for production_site in line.production_sites.values()
            if  not "ltn" in production_site.recipe.name
        ]
    )
    production_sites, entities = zip(*temp)
    entity_lookup = {site: entity for site, entity in temp}
    pprint(production_sites)
    # Now that we know the flow of goods, we can assign them to wagons by determining the order of machines
    production_sites, flows = create_cargo_wagon_assignment_problem(
        entities,
        global_input,
        production_sites,
        outputs=[product for factor, product in target_products],
    )
    blueprint_maker.make_blueprint(
        production_sites,
        ugly_reassignment=entity_lookup,
        output=[product for factor, product in target_products],
        flows=flows,
    )
    return line


if __name__ == "__main__":
    config_path = "block_maker.yaml"
    config = load_config(config_path)
    cargo_wagon_mall(config)
