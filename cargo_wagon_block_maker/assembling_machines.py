from collections import Counter

from draftsman.classes.group import Group
from draftsman.constants import Direction

from building_resolver import BuildingResolver
from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from recipe_provider import RecipeProvider


class AssemblingMachines:
    def __init__(self, modules, building_resolver: BuildingResolver, recipe_provider: RecipeProvider,**kwargs):
        self.modules = modules
        self.building_resolver = building_resolver
        self.recipe_provider = recipe_provider

    def build(self, blueprint, recipe_names, import_export, flows, **kwargs):
        assert len(recipe_names) % 8 == 0
        machines = [self.building_resolver(self.recipe_provider.by_name(recipe)) for recipe in recipe_names]
        machine_names = [machine.name for machine in machines]
        half = (len(recipe_names) / 2)
        # Put half the machines in top row, half in bottom row (y is 0 or 7)
        # Offset by assembling machine width in x direction
        machine_positions = [(3 * (i % half), (i // half) * 7) for i in range(len(recipe_names))]
        assert all(
            "productivity" in module for module in self.modules), "All modules must be productivity for now until we fix the building specific module inserter"
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
        g = AssemblingMachinesGroup(entities=entities, flows=flows, id='assembling_machines')
        for entity in g.entities:
            try:
                entity.import_export = import_export[entity.recipe]
            except:
                key = next(x for x in import_export.keys() if 'spm' in x)
                entity.import_export = import_export[key]
        g.translate(-2, 1)
        blueprint.entities.append(g)
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
            train_head: Group,
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
            self.add_circuit_connection('green', (3, i, 0), (1, f'circuit_{i}', 'plus_one'))
        self.assembling_machines = assembling_machines
        self.connectors = connectors
        self.wagons = wagons
        self.input_infrastructure = input_infrastructure
        self.output_infrastructure = output_infrastructure
        self.beacons = beacons
        self.power = power
