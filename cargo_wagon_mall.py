import json
from functools import partial
from pprint import pprint

from builders.building_resolver import build_building_resolver
from builders.recipe_transformations import build_recipe_transformations
from cargo_wagon_block_maker.assembling_machines import (
    AssemblingMachines,
)
from cargo_wagon_block_maker.blueprint_maker import BlueprintMaker
from cargo_wagon_block_maker.beacons import Beacons
from cargo_wagon_assignment_problem import create_cargo_wagon_assignment_problem
from cargo_wagon_block_maker.connectors import Connectors
from cargo_wagon_block_maker.input_infrastructure import InputInfrastructure
from cargo_wagon_block_maker.output_infrastructure import OutputInfrastructure
from cargo_wagon_block_maker.output_infrastructure_chest import OutputInfrastructureChest
from cargo_wagon_block_maker.power import Substations
from cargo_wagon_block_maker.train_head import TrainHead, LIQUIDS
from cargo_wagon_block_maker.train_head_one_liquids import TrainHeadOneLiquid
from cargo_wagon_block_maker.train_head_three_liquids import TrainHeadThreeLiquids
from cargo_wagon_block_maker.train_head_two_liquid import TrainHeadTwoLiquids
from cargo_wagon_block_maker.wagons import Wagons
from config.schema import CargoWagonMallConfig
from model_finalizer import CargoWagonMallProblem
from production_line_builder import ProductionLineBuilder
from recipe_provider_builder import (
    build_recipe_provider,
    apply_transformations, )

import yaml


def train_head_factory(liquids):
    cls = {
        0: TrainHead,
        1: TrainHeadOneLiquid,
        2: TrainHeadTwoLiquids,
        3: TrainHeadThreeLiquids,
    }
    return cls[len(liquids)](liquids=liquids)


def output_infrastructure_factory(output):
    cls = {
        "belt": OutputInfrastructure,
        "none": OutputInfrastructure,
        'chest': OutputInfrastructureChest,
    }
    return cls[output]()


def cargo_wagon_mall(config: CargoWagonMallConfig):
    target_products = config.target_products
    max_assemblers = config.max_assemblers
    # deal with buildings
    building_resolver_overrides = config.building_resolver_overrides
    assembly_loader = partial(
        lambda path: json.load(open(path)), config.assembly_path
    )
    recipe_loader = partial(lambda path: json.load(open(path)), config.recipe_path)

    assembly = assembly_loader()
    recipes = recipe_loader()

    building_resolver = build_building_resolver(assembly, building_resolver_overrides)
    recipe_provider = build_recipe_provider(recipes, building_resolver)
    recipe_transformations = build_recipe_transformations(config, building_resolver)

    try:
        for _, target_product in target_products:
            recipe_provider.by_name(target_product)
    except ValueError:
        raise ValueError(f"Recipe {target_product} not found")

    recipe_provider = apply_transformations(recipe_provider, recipe_transformations)
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

    temp = [
        entity
        for production_site in line.production_sites.values()
        if not "ltn" in production_site.recipe.name
        for entity in production_site.entities
    ]
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
    liquids = [input_fluid for input_fluid in global_input if input_fluid in LIQUIDS]
    blueprint_maker_modules = {
        "assembling_machines": AssemblingMachines(
            modules=config.assembling_machine_modules,
            building_resolver=building_resolver,
            recipe_provider=recipe_provider,
        ),
        "connectors": Connectors(),
        "wagons": Wagons(),
        "input_infrastructure": InputInfrastructure(),
        "power": Substations(),
        "output_infrastructure": output_infrastructure_factory(config.output),
        "beacons": Beacons(),
        "train_head": train_head_factory(liquids),
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    blueprint = blueprint_maker.make_blueprint(
        production_sites,
        entity_lookup=entity_lookup,
        output=[product for factor, product in target_products],
        flows=flows,
    )
    return blueprint


if __name__ == "__main__":
    # from draftsman.env import update
    # update(verbose=True,path='/Users/swozny/Library/Application Support/factorio/mods')  # equivalent to 'draftsman-update -v -p some/path'

    config_path = "config/stack_filter_inserters.yaml"

    with open(config_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    config = CargoWagonMallConfig(**yaml_data)
    cargo_wagon_mall(config)
