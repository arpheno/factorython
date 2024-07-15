import json
from functools import partial, cached_property
from pprint import pprint

from pydantic import BaseModel

from builders.building_resolver import build_building_resolver
from builders.recipe_transformations import build_recipe_transformations
from cargo_wagon_assignment_problem import CargoWagonAssignmentProblem
from cargo_wagon_block_maker.assembling_machines import (
    AssemblingMachines,
)
from cargo_wagon_block_maker.blueprint_maker import BlueprintMaker
from cargo_wagon_block_maker.beacons import Beacons
from cargo_wagon_block_maker.connectors import Connectors
from cargo_wagon_block_maker.input_infrastructure import InputInfrastructure
from cargo_wagon_block_maker.output_infrastructure import OutputInfrastructure
from cargo_wagon_block_maker.output_infrastructure_chest import OutputInfrastructureChest
from cargo_wagon_block_maker.power import Substations
from cargo_wagon_block_maker.roboports import Roboports
from cargo_wagon_block_maker.train_head import TrainHead, LIQUIDS
from cargo_wagon_block_maker.train_head_one_liquids import TrainHeadOneLiquid
from cargo_wagon_block_maker.train_head_three_liquids import TrainHeadThreeLiquids
from cargo_wagon_block_maker.train_head_two_liquid import TrainHeadTwoLiquids
from cargo_wagon_block_maker.wagons import Wagons
from config.schemas.schema import CargoWagonMallConfig
from model_finalizer import CargoWagonMallProblem
from production_line_builder import ProductionLineBuilder
from recipe_provider_builder import (
    build_recipe_provider,
    apply_transformations, )

import yaml


def train_head_factory(liquids, **kwargs):
    cls = {
        0: TrainHead,
        1: TrainHeadOneLiquid,
        2: TrainHeadTwoLiquids,
        3: TrainHeadThreeLiquids,
    }
    return cls[len(liquids)](liquids=liquids, **kwargs)


def output_infrastructure_factory(output):
    cls = {
        "belt": OutputInfrastructure,
        "none": OutputInfrastructure,
        'chest': OutputInfrastructureChest,
    }
    return cls[output]()


class MallMakerConfig(BaseModel):
    target_products: list
    max_assemblers: int
    assembly_path: str
    recipe_path: str
    building_resolver_overrides: dict
    solver: dict
    inserter_type: str
    inserter_capacity_bonus: int
    assembling_machine_modules: dict
    output: str


class MallMaker:
    def __init__(self, config: MallMakerConfig):
        self.config = config

        self.target_products = self.config.target_products
        self.max_assemblers = self.config.max_assemblers

        assembly = json.load(open(self.config.assembly_path))

        self.building_resolver = build_building_resolver(assembly, self.config.building_resolver_overrides)

        recipes = json.load(open(self.config.recipe_path))
        self._recipe_provider = build_recipe_provider(recipes, self.building_resolver)
        self._recipe_transformations = build_recipe_transformations(self.config, self.building_resolver)

    @cached_property
    def recipe_provider(self):
        result = apply_transformations(self._recipe_provider, self._recipe_transformations)
        return result
    def validate_self(self):
        for _, target_product in self.target_products:
            self.validate(target_product)
    def validate(self, product):
        try:
            self._recipe_provider.by_name(product)
        except ValueError:
            raise ValueError(f"Recipe {product} not found")

    def build_mall(self):

        for _, target_product in self.target_products:
            self.validate(target_product)

        assignment_problem_instance, line = self.build_optimal_ratios()

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
        production_sites, flows = assignment_problem_instance(
            entities,
            global_input,
            production_sites,
            outputs=[product for factor, product in self.target_products],
        )
        liquids = [input_fluid for input_fluid in global_input if input_fluid in LIQUIDS]
        blueprint_maker_modules = {
            "assembling_machines": AssemblingMachines(
                transformations=self.config.assembling_machine_modules,
                building_resolver=self.building_resolver,
                recipe_provider=self.recipe_provider,
            ),
            "connectors": Connectors(inserter_type=self.config.inserter_type,
                                     inserter_capacity_bonus_level=self.config.inserter_capacity_bonus),
            "wagons": Wagons(),
            "input_infrastructure": InputInfrastructure(),
            "power": Substations(),
            "roboports": Roboports(),
            "output_infrastructure": output_infrastructure_factory(self.config.output),
            "train_head": train_head_factory(liquids, inserter_type=self.config.inserter_type,
                                             inserter_capacity_bonus=self.config.inserter_capacity_bonus),
        }
        blueprint_maker = BlueprintMaker(
            modules=blueprint_maker_modules,
        )
        blueprint = blueprint_maker.make_blueprint(
            production_sites,
            entity_lookup=entity_lookup,
            output=[product for factor, product in self.target_products],
            flows=flows,
        )
        return blueprint

    def build_optimal_ratios(self):
        assignment_problem_instance = CargoWagonAssignmentProblem(**self.config.solver.dict())
        model_finalizer = CargoWagonMallProblem(
            self.target_products, max_assemblers=self.max_assemblers
        )
        # Determine the flow of goods through the production line
        production_line_builder = ProductionLineBuilder(
            self.recipe_provider, self.building_resolver, model_finalizer
        )
        line = production_line_builder.build()
        line.print()
        return assignment_problem_instance, line


if __name__ == "__main__":
    # from draftsman.env import update
    # update(verbose=True,path='/Users/swozny/Library/Application Support/factorio/mods')  # equivalent to 'draftsman-update -v -p some/path'

    config_path = "config/small_block_maker.yaml"

    with open(config_path, 'r') as file:
        yaml_data = yaml.safe_load(file)

    config = CargoWagonMallConfig(**yaml_data)

    mall_builder = CargoWagonMall(config)
    mall_builder.build_mall()
