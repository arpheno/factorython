from itertools import chain

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from typing import Dict

from building_resolver import BuildingResolver
from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from recipe_provider import RecipeProvider


def assembling_machines(recipe_names, import_export, building_resolver: BuildingResolver,
                        recipe_provider: RecipeProvider, flows):
    assert len(recipe_names) % 8 == 0
    machine_names = [building_resolver(recipe_provider.by_name(recipe)).name for recipe in recipe_names]
    half = (len(recipe_names) / 2)
    machine_positions = [(3 * (i % half), (i // half) * 7) for i in range(len(recipe_names))]
    entities = [
        {
            "name": machine,
            "recipe": recipe,
            "position": {"x": x, "y": y},
            "direction": Direction.NORTH if y == 0 else Direction.SOUTH,
        }
        for (x, y), machine, recipe in zip(machine_positions, machine_names, recipe_names)
    ]
    g = AssemblingMachinesGroup(entities=entities, flows=flows)
    for entity in g.entities:
        entity.import_export = import_export[entity.recipe]

    g.translate(-2, 1)
    return g


class ProductionLine(Group):
    def __init__(
            self,
            *,
            assembling_machines: AssemblingMachinesGroup,
            connectors: Group,
            wagons: Group,
            input_infrastructure: Group,
            power: Group,
            output_infrastructure: Group,
            beacons: Group,
            roboports: Group,
            lights=Group,
            entities: Group = [],
            **kwargs,
    ):
        all_groups = [
            wagons,
            connectors,
            assembling_machines,
            input_infrastructure,
            output_infrastructure,
            power,
            beacons,
            roboports,
            lights
        ]
        for group in all_groups[2:]:
            group.translate(-1, 0)
        super(ProductionLine, self).__init__(
            **kwargs, entities=all_groups
        )
        self.assembling_machines = assembling_machines
        self.connectors = connectors
        self.wagons = wagons
        self.input_infrastructure = input_infrastructure
        self.output_infrastructure = output_infrastructure
        self.beacons = beacons
        self.power = power


class BlueprintMaker:
    def __init__(
            self,
            modules: Dict[str, BlueprintMakerModule],
            building_resolver: BuildingResolver,
            recipe_provider: RecipeProvider
    ):
        self.modules = modules
        self.building_resolver = building_resolver
        self.recipe_provider = recipe_provider

    def make_blueprint(self, recipes, output, ugly_reassignment, flows):
        # recipes is in a form of grouped recipes by 4, so the first two apply to the top row, the second two to the bottom row of a group of 4
        # i need to reshape this into a list of recipes, where the first half is the top row, the second half is the bottom row for the entire row
        # yield chunks of 4 recipes
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        # Oh god the horror
        mrecipes = list(chain.from_iterable(zip(chunks(recipes, 2))))
        mrecipes = list(chain.from_iterable(mrecipes[::2])) + list(chain.from_iterable(mrecipes[1::2]))
        assembling_machines = self.modules['assembling_machines'](mrecipes, ugly_reassignment, self.building_resolver,
                                                                  self.recipe_provider, flows)
        stuff = {entity_type: module.build(assembling_machines, output) for entity_type, module in self.modules.items()
                 if not entity_type == 'assembling_machines'}
        b = Blueprint()
        g = ProductionLine(assembling_machines=assembling_machines, **stuff)
        b.entities.append(g)
        b.generate_power_connections(only_axis=True)
        print(b.to_string())
        return g


if __name__ == "__main__":
    b = Blueprint()
    b.entities.append(
        assembling_machines(["assembling-machine-3"] * 8, ["copper-cable"] * 8)
    )
    print(b.to_string())
