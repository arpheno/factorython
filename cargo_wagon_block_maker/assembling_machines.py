from collections import Counter
from itertools import chain

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from typing import Dict

from building_resolver import BuildingResolver
from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from recipe_provider import RecipeProvider


class AssemblingMachines:
    def __init__(self, modules, building_resolver: BuildingResolver, recipe_provider: RecipeProvider):
        self.modules = modules
        self.building_resolver = building_resolver
        self.recipe_provider = recipe_provider

    def build(self, recipe_names, import_export, flows,**kwargs):
        assert len(recipe_names) % 8 == 0
        machines = [self.building_resolver(self.recipe_provider.by_name(recipe)) for recipe in recipe_names]
        machine_names = [machine.name for machine in machines]
        half = (len(recipe_names) / 2)
        # Put half the machines in top row, half in bottom row (y is 0 or 7)
        # Offset by assembling machine width in x direction
        machine_positions = [(3 * (i % half), (i // half) * 7) for i in range(len(recipe_names))]
        entities = [
            {
                "name": machine,
                "recipe": recipe,
                "position": {"x": x, "y": y},
                "items": dict(Counter(self.modules)),
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
            train_head:Group,
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
            train_head,
        ]
        # for group in all_groups[2:]:
        #     group.translate(-1, 0)
        super(ProductionLine, self).__init__(
            **kwargs, entities=all_groups
        )
        for i, _ in enumerate(assembling_machines.groups):
            self.add_circuit_connection('green', (4, i, 0), (1, f'circuit_{i}', 'minus_one'))
            self.add_circuit_connection('green', (3, i, 0), (1, f'circuit_{i}', 'plus_one'))
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
    ):
        self.modules = modules

    def make_blueprint(self, recipes, output, ugly_reassignment, flows):
        # recipes is in a form of grouped recipes by 4, so the first two apply to the top row, the second two to the bottom row of a group of 4
        # i need to reshape this into a list of recipes, where the first half is the top row, the second half is the bottom row for the entire row
        # yield chunks of 4 recipes
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        # Oh god the horror

        # This reshapes the top/bottom row enumeration of machines into a grouped enumeration of machines
        # This is necessary because the decision making model works on groups and i'm too lazy to change it
        # to the top/bottom row enumeration
        mrecipes = list(chain.from_iterable(zip(chunks(recipes, 2))))
        mrecipes = list(chain.from_iterable(mrecipes[::2])) + list(chain.from_iterable(mrecipes[1::2]))
        default_build_args = dict(
            recipe_names=mrecipes,
            import_export=ugly_reassignment,
            flows=flows,
            outputs=output,
        )

        b = Blueprint()
        built_modules = {}
        for key, module in self.modules.items():
            built_modules[key] = module.build(**default_build_args,**built_modules)
        g = ProductionLine(**built_modules)
        b.entities.append(g)
        b.generate_power_connections(only_axis=True)
        print(b.to_string())
        return g
