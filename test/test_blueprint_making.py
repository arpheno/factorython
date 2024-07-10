import json
from functools import partial

import pytest
import yaml
from draftsman.classes.blueprint import Blueprint

from cargo_wagon_block_maker.assembling_machines import AssemblingMachines
from cargo_wagon_block_maker.beacons import Beacons
from cargo_wagon_block_maker.blueprint_maker import BlueprintMaker
from cargo_wagon_block_maker.connectors import Connectors
from cargo_wagon_block_maker.input_infrastructure import InputInfrastructure
from cargo_wagon_block_maker.power import Substations
from cargo_wagon_block_maker.wagons import Wagons
from cargo_wagon_mall import train_head_factory, output_infrastructure_factory
from builders.building_resolver import build_building_resolver
from config.schema import CargoWagonMallConfig
from recipe_provider_builder import build_recipe_provider


@pytest.fixture
def recorded_data():
    data = {
        "target_products": [
            (2, "rail"),
            (1, "cargo-wagon"),
            (4, "stack-filter-inserter"),
            (4, "assembling-machine-2")
        ],
        "production_sites": [
            "motor",
            "iron-gear-wheel",
            "burner-assembling-machine",
            "iron-gear-wheel",
            "copper-cable",
            "iron-gear-wheel",
            "electric-motor",
            "copper-cable",
            "copper-cable",
            "assembling-machine-1",
            "stone-tablet",
            "electronic-circuit-stone",
            "advanced-circuit",
            "cargo-wagon",
            "iron-gear-wheel",
            "plastic-bar",
            "copper-cable",
            "electronic-circuit-stone",
            "copper-cable",
            "advanced-circuit",
            "burner-inserter",
            "inserter",
            "iron-stick",
            "rail",
            "stack-inserter",
            "electronic-circuit-stone",
            "fast-inserter",
            "copper-cable",
            "electronic-circuit-stone",
            "stack-filter-inserter",
            "assembling-machine-2",
            "copper-cable"
        ],
        "entity_lookup": {
            "advanced-circuit": {
                "electronic-circuit": -0.8333333333333334,
                "copper-cable": -1.6666666666666667,
                "advanced-circuit": 0.5166666666666667,
                "plastic-bar": -0.8333333333333334
            },
            "assembling-machine-1": {
                "burner-assembling-machine": -0.9415799189999999,
                "iron-gear-wheel": -3.7663196759999997,
                "electric-motor": -0.9415799189999999,
                "assembling-machine-1": 0.9415799189999999
            },
            "assembling-machine-2": {
                "steel-plate": -1.8831598379999999,
                "electric-motor": -1.8831598379999999,
                "assembling-machine-2": 0.9415799189999999,
                "electronic-circuit": -1.8831598379999999,
                "assembling-machine-1": -0.9415799189999999
            },
            "burner-assembling-machine": {
                "iron-plate": -7.5326393519999995,
                "stone-brick": -3.7663196759999997,
                "motor": -0.9415799189999999,
                "burner-assembling-machine": 0.9415799189999999
            },
            "burner-inserter": {
                "iron-stick": -1.8831598379999999,
                "motor": -0.9415799189999999,
                "burner-inserter": 0.9415799189999999
            },
            "cargo-wagon": {
                "iron-plate": -4.707899595,
                "iron-gear-wheel": -2.3539497975,
                "steel-plate": -4.707899595,
                "cargo-wagon": 0.23539497974999998
            },
            "copper-cable": {
                "copper-cable": 7.157461039999995,
                "copper-plate": -2.886072999999998
            },
            "electric-motor": {
                "iron-plate": -3.0373545625,
                "iron-gear-wheel": -3.0373545625,
                "electric-motor": 3.7663196575,
                "copper-cable": -18.224127375000002
            },
            "fast-inserter": {
                "iron-plate": -1.8831598379999999,
                "electronic-circuit": -1.8831598379999999,
                "fast-inserter": 0.9415799189999999,
                "inserter": -0.9415799189999999
            },
            "inserter": {
                "electric-motor": -0.9415799189999999,
                "burner-inserter": -0.9415799189999999,
                "inserter": 0.9415799189999999
            },
            "iron-gear-wheel": {
                "iron-plate": -10.0,
                "iron-gear-wheel": 6.2
            },
            "iron-stick": {
                "iron-plate": -0.85425595,
                "iron-stick": 2.118554756
            },
            "motor": {
                "iron-plate": -1.5186772916666669,
                "iron-gear-wheel": -1.5186772916666669,
                "motor": 1.8831598416666668
            },
            "plastic-bar": {
                "petroleum-gas": -14.124293850000003,
                "coal": -0.7062146925000001,
                "plastic-bar": 1.6666666743000003
            },
            "rail": {
                "stone": -0.2353949745,
                "steel-plate": -0.2353949745,
                "iron-stick": -0.2353949745,
                "rail": 0.470789949
            },
            "stack-filter-inserter": {
                "stack-filter-inserter": 0.9415799189999999,
                "electronic-circuit": -4.707899595,
                "stack-inserter": -0.9415799189999999
            },
            "stack-inserter": {
                "stack-inserter": 0.9415799189999999,
                "fast-inserter": -0.9415799189999999,
                "electronic-circuit": -14.123698785,
                "iron-gear-wheel": -14.123698785,
                "advanced-circuit": -0.9415799189999999
            },
            "stone-tablet": {
                "stone-tablet": 20.999054536,
                "stone-brick": -4.23368035
            },
            "electronic-circuit-stone": {
                "electronic-circuit": 6.2,
                "stone-tablet": -5.0,
                "copper-cable": -15.0
            }
        },
        "flows": [
            {
                "steel-plate": 6.8264544,
                "electric-motor": 0.0,
                "fast-inserter": 0.0,
                "coal": 0.70621469,
                "burner-assembling-machine": 0.0,
                "electronic-circuit": 0.0,
                "copper-cable": 0.0,
                "burner-inserter": 0.0,
                "iron-plate": 59.533987,
                "advanced-circuit": 0.0,
                "assembling-machine-1": 0.0,
                "stack-inserter": 0.0,
                "iron-stick": 0.0,
                "stone": 0.23539497,
                "petroleum-gas": 14.124294,
                "stone-brick": 8.0,
                "inserter": 0.0,
                "iron-gear-wheel": 0.0,
                "copper-plate": 32.886073,
                "plastic-bar": 0.0,
                "stone-tablet": 0.0,
                "motor": 0.0
            },
            {
                "steel-plate": 6.8264544,
                "electric-motor": 0.0,
                "fast-inserter": 0.0,
                "coal": 0.70621469,
                "burner-assembling-machine": 0.94157992,
                "electronic-circuit": 0.0,
                "copper-cable": 0.0,
                "burner-inserter": 0.0,
                "iron-plate": 30.48267,
                "advanced-circuit": 0.0,
                "assembling-machine-1": 0.0,
                "stack-inserter": 0.0,
                "iron-stick": 0.0,
                "stone": 0.23539497,
                "petroleum-gas": 14.124294,
                "stone-brick": 4.2336803,
                "inserter": 0.0,
                "iron-gear-wheel": 10.881323,
                "copper-plate": 32.886073,
                "plastic-bar": 0.0,
                "stone-tablet": 0.0,
                "motor": 0.94157992
            },
            {
                "steel-plate": 6.8264544,
                "electric-motor": 3.7663197,
                "fast-inserter": 0.0,
                "coal": 0.70621469,
                "burner-assembling-machine": 0.94157992,
                "electronic-circuit": 0.0,
                "copper-cable": 6.5758723,
                "burner-inserter": 0.0,
                "iron-plate": 17.445315,
                "advanced-circuit": 0.0,
                "assembling-machine-1": 0.0,
                "stack-inserter": 0.0,
                "iron-stick": 0.0,
                "stone": 0.23539497,
                "petroleum-gas": 14.124294,
                "stone-brick": 4.2336803,
                "inserter": 0.0,
                "iron-gear-wheel": 14.043968,
                "copper-plate": 22.886073,
                "plastic-bar": 0.0,
                "stone-tablet": 0.0,
                "motor": 0.94157992
            },
            {
                "steel-plate": 6.8264544,
                "electric-motor": 2.8247398,
                "fast-inserter": 0.0,
                "coal": 0.70621469,
                "burner-assembling-machine": 0.0,
                "electronic-circuit": 5.6645847,
                "copper-cable": 3.9758723,
                "burner-inserter": 0.0,
                "iron-plate": 17.445315,
                "advanced-circuit": 0.0,
                "assembling-machine-1": 0.94157992,
                "stack-inserter": 0.0,
                "iron-stick": 0.0,
                "stone": 0.23539497,
                "petroleum-gas": 14.124294,
                "stone-brick": 0.0,
                "inserter": 0.0,
                "iron-gear-wheel": 10.277648,
                "copper-plate": 17.886073,
                "plastic-bar": 0.0,
                "stone-tablet": 15.0,
                "motor": 0.94157992
            },
            {
                "steel-plate": 2.1185548,
                "electric-motor": 2.8247398,
                "fast-inserter": 0.0,
                "coal": 0.0,
                "burner-assembling-machine": 0.0,
                "electronic-circuit": 4.8312514,
                "copper-cable": 2.3092056,
                "burner-inserter": 0.0,
                "iron-plate": 2.7374158,
                "advanced-circuit": 0.42491325,
                "assembling-machine-1": 0.94157992,
                "stack-inserter": 0.0,
                "iron-stick": 0.0,
                "stone": 0.23539497,
                "petroleum-gas": 0.0,
                "stone-brick": 0.0,
                "inserter": 0.0,
                "iron-gear-wheel": 14.123699,
                "copper-plate": 17.886073,
                "plastic-bar": 0.83333333,
                "stone-tablet": 15.0,
                "motor": 0.94157992
            },
            {
                "steel-plate": 2.1185548,
                "electric-motor": 2.8247398,
                "fast-inserter": 0.0,
                "coal": 0.0,
                "burner-assembling-machine": 0.0,
                "electronic-circuit": 10.197918,
                "copper-cable": 10.442539,
                "burner-inserter": 0.0,
                "iron-plate": 2.7374158,
                "advanced-circuit": 0.94157992,
                "assembling-machine-1": 0.94157992,
                "stack-inserter": 0.0,
                "iron-stick": 0.0,
                "stone": 0.23539497,
                "petroleum-gas": 0.0,
                "stone-brick": 0.0,
                "inserter": 0.0,
                "iron-gear-wheel": 14.123699,
                "copper-plate": 7.886073,
                "plastic-bar": 0.0,
                "stone-tablet": 10.0,
                "motor": 0.94157992
            },
            {
                "steel-plate": 1.8831598,
                "electric-motor": 1.8831598,
                "fast-inserter": 0.0,
                "coal": 0.0,
                "burner-assembling-machine": 0.0,
                "electronic-circuit": 10.197918,
                "copper-cable": 10.442539,
                "burner-inserter": 0.0,
                "iron-plate": 1.8831598,
                "advanced-circuit": 0.94157992,
                "assembling-machine-1": 0.94157992,
                "stack-inserter": 0.0,
                "iron-stick": 0.0,
                "stone": 0.0,
                "petroleum-gas": 0.0,
                "stone-brick": 0.0,
                "inserter": 0.94157992,
                "iron-gear-wheel": 14.123699,
                "copper-plate": 7.886073,
                "plastic-bar": 0.0,
                "stone-tablet": 10.0,
                "motor": 0.0
            },
            {
                "steel-plate": 1.8831598,
                "electric-motor": 1.8831598,
                "fast-inserter": 0.0,
                "coal": 0.0,
                "burner-assembling-machine": 0.0,
                "electronic-circuit": 0.39105943,
                "copper-cable": 2.6,
                "burner-inserter": 0.0,
                "iron-plate": 0.0,
                "advanced-circuit": 0.0,
                "assembling-machine-1": 0.94157992,
                "stack-inserter": 0.94157992,
                "iron-stick": 0.0,
                "stone": 0.0,
                "petroleum-gas": 0.0,
                "stone-brick": 0.0,
                "inserter": 0.0,
                "iron-gear-wheel": 0.0,
                "copper-plate": 5.0,
                "plastic-bar": 0.0,
                "stone-tablet": 5.0,
                "motor": 0.0
            }
        ]
    }
    return data


@pytest.fixture
def config():
    with open('../config/block_maker.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file)
    config = CargoWagonMallConfig(**yaml_data)
    config.assembly_path = f'../{config.assembly_path}'
    config.recipe_path = f'../{config.recipe_path}'
    return config


def test_make_blueprint(recorded_data, config):
    # Assuming BlueprintMaker is a mockable class
    target_products = config.target_products
    building_resolver_overrides = config.building_resolver_overrides
    assembly_loader = partial(
        lambda path: json.load(open(path)), config.assembly_path
    )
    recipe_loader = partial(lambda path: json.load(open(path)), config.recipe_path)

    assembly = assembly_loader()
    recipes = recipe_loader()

    building_resolver = build_building_resolver(assembly, building_resolver_overrides)
    recipe_provider = build_recipe_provider(recipes, building_resolver)
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
        "train_head": train_head_factory(config.output),
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    production_sites = recorded_data["production_sites"]
    entity_lookup = recorded_data["entity_lookup"]
    flows = recorded_data["flows"]
    blueprint = blueprint_maker.make_blueprint(
        production_sites,
        entity_lookup=entity_lookup,
        output=[product for factor, product in target_products],
        flows=flows,
    )

    # Assert the function was called as expected (use a mock library if needed)
    assert isinstance(blueprint, Blueprint)
    print(blueprint.to_string())
def test_make_blueprint_one_liquid(recorded_data, config):
    # Assuming BlueprintMaker is a mockable class
    target_products = config.target_products
    config.output.liquids=['petroleum-gas']
    building_resolver_overrides = config.building_resolver_overrides
    assembly_loader = partial(
        lambda path: json.load(open(path)), config.assembly_path
    )
    recipe_loader = partial(lambda path: json.load(open(path)), config.recipe_path)

    assembly = assembly_loader()
    recipes = recipe_loader()

    building_resolver = build_building_resolver(assembly, building_resolver_overrides)
    recipe_provider = build_recipe_provider(recipes, building_resolver)
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
        "train_head": train_head_factory(config.output),
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    production_sites = recorded_data["production_sites"]
    entity_lookup = recorded_data["entity_lookup"]
    flows = recorded_data["flows"]
    blueprint = blueprint_maker.make_blueprint(
        production_sites,
        entity_lookup=entity_lookup,
        output=[product for factor, product in target_products],
        flows=flows,
    )

    # Assert the function was called as expected (use a mock library if needed)
    assert isinstance(blueprint, Blueprint)
    print(blueprint.to_string())
def test_make_blueprint_two_liquids(recorded_data, config):
    # Assuming BlueprintMaker is a mockable class
    target_products = config.target_products
    config.output.liquids=['petroleum-gas','light-oil']
    building_resolver_overrides = config.building_resolver_overrides
    assembly_loader = partial(
        lambda path: json.load(open(path)), config.assembly_path
    )
    recipe_loader = partial(lambda path: json.load(open(path)), config.recipe_path)

    assembly = assembly_loader()
    recipes = recipe_loader()

    building_resolver = build_building_resolver(assembly, building_resolver_overrides)
    recipe_provider = build_recipe_provider(recipes, building_resolver)
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
        "train_head": train_head_factory(config.output),
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    production_sites = recorded_data["production_sites"]
    entity_lookup = recorded_data["entity_lookup"]
    flows = recorded_data["flows"]
    blueprint = blueprint_maker.make_blueprint(
        production_sites,
        entity_lookup=entity_lookup,
        output=[product for factor, product in target_products],
        flows=flows,
    )

    # Assert the function was called as expected (use a mock library if needed)
    assert isinstance(blueprint, Blueprint)
    print(blueprint.to_string())
def test_make_blueprint_three_liquids(recorded_data, config):
    # Assuming BlueprintMaker is a mockable class
    target_products = config.target_products
    config.output.liquids=['petroleum-gas','light-oil','water']
    building_resolver_overrides = config.building_resolver_overrides
    assembly_loader = partial(
        lambda path: json.load(open(path)), config.assembly_path
    )
    recipe_loader = partial(lambda path: json.load(open(path)), config.recipe_path)

    assembly = assembly_loader()
    recipes = recipe_loader()

    building_resolver = build_building_resolver(assembly, building_resolver_overrides)
    recipe_provider = build_recipe_provider(recipes, building_resolver)
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
        "train_head": train_head_factory(config.output),
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    production_sites = recorded_data["production_sites"]
    entity_lookup = recorded_data["entity_lookup"]
    flows = recorded_data["flows"]
    blueprint = blueprint_maker.make_blueprint(
        production_sites,
        entity_lookup=entity_lookup,
        output=[product for factor, product in target_products],
        flows=flows,
    )

    # Assert the function was called as expected (use a mock library if needed)
    assert isinstance(blueprint, Blueprint)
    print(blueprint.to_string())
