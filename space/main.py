import json
from math import ceil
from pprint import pprint

from draftsman.classes.blueprint import Blueprint
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
from cargo_wagon_block_maker.lights import Lights
from cargo_wagon_block_maker.output_infrastructure import OutputInfrastructure
from cargo_wagon_block_maker.power import MediumPowerPoles, Substations
from cargo_wagon_block_maker.roboports import Roboports
from cargo_wagon_block_maker.wagons import Wagons
from model_finalizer import CargoWagonProblem
from module import ModuleBuilder, Module
from module_inserter import insert_module
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import build_recipe_provider
from space.machine import robot_connected_space_machine


def main():
    available_resources = ["electronic-circuit", "advanced-circuit", "electric-motor"]
    available_resources = []
    building_resolver_overrides = {
        "crafting": "assembling-machine-3",
        "basic-crafting": "assembling-machine-3",
        "crafting-with-fluid": "assembling-machine-3",
        "advanced-crafting": "assembling-machine-3",
        'chemistry':'chemical-plant',
        'pulverising':'assembling-machine-3'
        # 'kiln':'electric-furnace',
    }
    target_product = 'nuclear-reactor'#"se-rocket-science-pack"
    max_assemblers=32
    # deal with buildings
    assembly_path = "../data/assembly_machine.json"
    recipes_path = "../data/recipes.json"
    beacon_modules = ["speed-module-2"] * 8
    assembling_machine_modules = ["productivity-module-2"] * 4

    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories,
        overrides=building_resolver_overrides,
    )

    recipe_provider = build_recipe_provider(recipes_path, available_resources)
    try:
        recipe_provider.by_name(target_product)
    except:
        print(f"Could not find recipe for {target_product}")
        print("Available recipes:")
        for recipe in recipe_provider.name_includes(target_product):
            print(recipe.name)
        raise Exception("Recipe not found")

    module_builder = ModuleBuilder(modules)
    # m=robot_connected_space_machine(building_resolver,recipe_provider,'se-genetic-data')
    # m=robot_connected_space_machine(building_resolver,recipe_provider,'se-biochemical-resistance-data')
    # m=robot_connected_space_machine(building_resolver,recipe_provider,'se-biochemical-data')
    m=robot_connected_space_machine(building_resolver,recipe_provider,'se-space-water')
    b=Blueprint()
    b.entities.append(m)
    print(b.to_string())
if __name__ == '__main__':
    main()