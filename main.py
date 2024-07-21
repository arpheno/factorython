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
    apply_transformers,
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
        overrides={"chemistry": "chemical-plant",
                   'crafting': 'assembling-machine-1',
                   'advanced-crafting': 'assembling-machine-1',
                   'basic-crafting': 'assembling-machine-1',
                   'space-supercomputing-1': 'se-space-supercomputer-1',
                   'space-supercomputing-2': 'se-space-supercomputer-2',
                   },
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
                "se-space-coolant-supercooled",
                "se-cryonite-rod",
                "se-vitamelange",
                # "se-vitamelange-spice",
                # 'se-vitamelange-extract',
                "se-vulcanite-block",
                "se-core-fragment-se-vitamelange",
                'se-iridium-ingot',
                'se-heavy-bearing',
                'se-heavy-girder',
                'se-beryllium-ingot',
                'se-bio-sludge',
                'sulfur',
                'se-heavy-composite',
                'se-significant-data',
                'se-iron-ingot'
                'se-copper-ingot',
                'se-holmium-ingot',
                'uranium-235',
                'se-heat-shielding',
                'se-ion-stream',
                'se-particle-stream',
                'advanced-circuit',
                'concrete',
                'low-density-structure',
                'electronic'
            ]
        ),
        # BuildingSpecificModuleInserter(
        #     {"productivity": "productivity-module-2", "speed": "speed-module-2"},
        #     building_resolver,
        #     beacon_type="small",
        # ),

    ]
    recipe_provider = apply_transformers(recipe_provider, recipe_transformations)
    time_running = 60*15
    # target = [('se-vitamelange-extract', 3.4)]
    # target = [('electric-mining-drill', 1),('inserter',10),('transport-belt',10),('assembling-machine-1',5)]
    # v = 0.77/10*(15/13.86)*(15/18.92)

    # target = [(a, b * v) for a, b in target]
    target = [('automation-science-pack', 2200/time_running), ('logistic-science-pack', 1300/time_running)]
    # recipe_provider.verify(target[0][0])
    model_finalizer = ProductionLineProblem(
        # [("se-cryonite-rod", 2000.0 / time_running)]
        # [("se-vulcanite-block", 15.0 / time_running)]
        target
    )
    production_line_builder = ProductionLineBuilder(
        recipe_provider, building_resolver, model_finalizer
    )
    line = production_line_builder.build()
    line.print()
    # line.print(duration=time_running)


if __name__ == "__main__":
    main()
