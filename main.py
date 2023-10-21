import json
import math
from itertools import chain

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.data.modules import raw as modules

from building_resolver import BuildingResolver
from materials import se_materials, minable_resources, basic_processing
from model_finalizer import ProductionLineProblem
from module import Module, ModuleBuilder
from module_inserter import PrimitiveModuleInserter, BuildingSpecificModuleInserter
from production_line import ProductionLine
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from recipe_provider_builder import (
    build_recipe_provider,
    FreeRecipesAdder,
    apply_transformations,
    RecipesRemover,
    Barreler,
)
from space.machine import robot_connected_space_machine


class PrimitiveLayouter:
    def layout(self, machines: [Group]):
        group = Group()
        square_length = next(x for x in range(10) if x * x >= len(machines))
        rows = [Group() for _ in range(square_length)]
        for i, machine in enumerate(machines):
            g = rows[i // square_length]
            max_x = max(
                [
                    (e.global_position["x"], e.tile_width // 2 + 1, e.name)
                    for e in g.find_entities_filtered()
                ]
                + [(0, 0)]
            )
            min_local_x = min(
                [
                    (e.global_position["x"], +e.tile_width // 2 + 1, e.name)
                    for e in machine.find_entities_filtered()
                ]
            )
            original_x_coordinate = math.ceil(
                max_x[0] + max_x[1] + abs(min_local_x[0]) + min_local_x[1]
            )
            machine.translate(original_x_coordinate, 0)
            g.entities.append(machine)
        for i, row in enumerate(rows):
            row.translate(0, 20 * i)
            group.entities.append(row)
        return group


def main():
    # deal with buildings
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    building_resolver = BuildingResolver(
        crafting_categories,
        overrides={"chemistry": "chemical-plant"},
    )
    # deal with recipes
    recipes_path = "data/recipes.json"
    recipe_provider = build_recipe_provider(recipes_path)

    recipe_transformations = [
        # FreeRecipesAdder(se_materials),
        FreeRecipesAdder(minable_resources),
        FreeRecipesAdder(basic_processing),
        RecipesRemover([f"se-formatting-{x}" for x in range(2, 5)]),
        Barreler(["petroleum-gas", "lubricant"]),
        FreeRecipesAdder(
            [
                "advanced-circuit",
                "se-space-coolant-warm",
                "se-cryonite",
                "se-vitamelange",
                "se-vulcanite-block",
            ]
        ),
        BuildingSpecificModuleInserter(
            {"productivity": "productivity-module-3", "speed": "speed-module-3"},
            building_resolver,
            beacon_type="small",
        ),
    ]
    recipe_provider = apply_transformations(recipe_provider, recipe_transformations)
    time_running = 600

    model_finalizer = ProductionLineProblem(
        # [("se-cryonite-rod", 2000.0 / time_running)]
        [("se-vitalic-reagent", 2000.0 / time_running)]
    )
    production_line_builder = ProductionLineBuilder(
        recipe_provider, building_resolver, model_finalizer
    )
    line = production_line_builder.build()
    line.print()
    # line.print(duration=time_running)


if __name__ == "__main__":
    main()
