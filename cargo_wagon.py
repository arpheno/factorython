import json
from math import ceil
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
from cargo_wagon_block_maker.power import  Substations
from cargo_wagon_block_maker.wagons import Wagons
from materials import  minable_resources, basic_processing
from model_finalizer import CargoWagonProblem
from module import ModuleBuilder, Module
from module_inserter import PrimitiveModuleInserter
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import (
    build_recipe_provider,
    FreeRecipesAdder,
    RecipesRemover,
    apply_transformations,
)


def main():
    available_resources = []
    building_resolver_overrides = {
        "crafting": "assembling-machine-3",
        "basic-crafting": "assembling-machine-3",
        "crafting-with-fluid": "assembling-machine-3",
        "advanced-crafting": "assembling-machine-3",
        "chemistry": "chemical-plant",
        "pulverising": "assembling-machine-3"
        # 'kiln':'electric-furnace',
    }
    target_product = "se-delivery-cannon-capsule"  # "se-rocket-science-pack"
    target_product = "satellite"  # "se-rocket-science-pack"
    max_assemblers = 32
    # deal with buildings
    assembly_path = "data/assembly_machine.json"
    recipes_path = "data/recipes.json"
    beacon_modules = ["speed-module-2"] * 8
    assembling_machine_modules = ["productivity-module-2"] * 4

    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories,
        overrides=building_resolver_overrides,
    )

    recipe_provider = build_recipe_provider(recipes_path)
    recipe_provider.by_name(target_product)
    module_builder = ModuleBuilder(modules)

    recipe_transformations = [
        FreeRecipesAdder(minable_resources),
        FreeRecipesAdder(basic_processing),
        PrimitiveModuleInserter(
            dict(
                productivity=sum(
                    (
                        module_builder.build(module)
                        for module in assembling_machine_modules
                    ),
                    Module(name="productivity", productivity=0),
                )
                + sum(
                    (module_builder.build(module) for module in beacon_modules),
                    Module(name="speed", speed=0),
                )
                * 0.5,
                speed=sum(
                    (module_builder.build(module) for module in beacon_modules),
                    Module(name="speed", speed=0),
                )
                * 0.5,
            )
        )
        # FreeRecipesAdder(['advanced-circuit', 'se-space-coolant-warm']),
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
        # "roboports": Roboports(),
        # "lights": Lights(),
    }
    blueprint_maker = BlueprintMaker(
        modules=blueprint_maker_modules,
    )
    model_finalizer = CargoWagonProblem([target_product], max_assemblers=max_assemblers)

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
            for q in range(ceil(production_site.quantity)):
                production_sites.append(production_site.recipe.name)
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
                entity = {
                    good: products.get(good, 0) * rate + ingredients.get(good, 0) * rate
                    for good in products.keys() | ingredients.keys()
                }
                entities.append(entity)
        else:
            global_input[
                production_site.recipe.products[0].name
            ] = production_site.quantity
    pprint(production_sites)
    # if len(global_input)>4:
    #     raise Exception("This production line would require more than 4 pre-made things, but we only have 4 slots")
    ugly_reassignment = {}
    for site, entity in zip(production_sites, entities):
        ugly_reassignment[site] = entity
    # Now that we know the flow of goods, we can assign them to wagons by determining the order of machines
    production_sites, flows = create_cargo_wagon_assignment_problem(
        entities, global_input, production_sites, outputs=[target_product]
    )
    pprint(flows)
    # cargo_wagon_blueprint(production_sites, ugly_reassignment, output=target_product, flows=flows)
    blueprint_maker.make_blueprint(
        production_sites,
        ugly_reassignment=ugly_reassignment,
        output=target_product,
        flows=flows,
    )
    return line


if __name__ == "__main__":
    main()
