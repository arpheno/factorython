from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import inserters
from draftsman.prototypes.inserter import Inserter

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule


def mixed_belt_input():
    g = Group(entities=[{'name': 'transport-belt',
                        'position': {'x': 0.0, 'y': 0.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt',
                        'position': {'x': 0.0, 'y': -1.0},
                        'direction': Direction.SOUTH},
                       {'name': 'transport-belt',
                        'position': {'x': -1.0, 'y': -1.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt',
                        'position': {'x': 1.0, 'y': 0.0},
                        'direction': Direction.SOUTH},
                       {'name': 'transport-belt',
                        'position': {'x': -1.0, 'y': 2.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt',
                        'position': {'x': 0.0, 'y': 2.0},
                        'direction': Direction.SOUTH},
                       {'name': 'transport-belt', 'position': {'x': 0.0, 'y': 1.0}},
                       {'name': 'transport-belt',
                        'position': {'x': -1.0, 'y': 1.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt',
                        'position': {'x': 2.0, 'y': 2.0},
                        'direction': Direction.EAST},
                        {'name': 'transport-belt',
                         'position': {'x': 2.0, 'y': 1.0},
                         'direction': Direction.EAST},
                        {'name': 'transport-belt',
                         'position': {'x': 3.0, 'y': 2.0},
                         'direction': Direction.EAST},
                        {'name': 'transport-belt',
                         'position': {'x': 3.0, 'y': 1.0},
                         'direction': Direction.EAST},
                       {'name': 'transport-belt',
                        'position': {'x': 1.0, 'y': 2.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt',
                        'position': {'x': 1.0, 'y': 1.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt',
                        'position': {'x': -1.0, 'y': 4.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt', 'position': {'x': 0.0, 'y': 4.0}},
                       {'name': 'transport-belt',
                        'position': {'x': 0.0, 'y': 3.0},
                        'direction': Direction.EAST},
                       {'name': 'transport-belt', 'position': {'x': 1.0, 'y': 3.0}}])
    return g


class InputInfrastructure(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        g = Group(entities=[

            # if the building is facing south, place the input infrastructure to the north
            {
                "name": "fast-inserter",
                "position": {
                    "x": machine.global_position["x"],
                    "y": machine.global_position["y"] - 2 if machine.direction == Direction.SOUTH else
                    machine.global_position["y"] + 2,
                },
                "direction": Direction.SOUTH
                if machine.direction == Direction.NORTH
                else Direction.NORTH,
            }
            for machine in assembling_machines.entities])
        machine = assembling_machines.top_row[0]
        g.entities.append(
            Inserter(**{
                'name': 'miniloader-inserter',
                'position': {'x': machine.global_position['x'] - 1, 'y': machine.global_position['y'] + 3},
                'direction': Direction.EAST
            }))
        g.entities.append(
            Inserter(**{
                'name': 'miniloader-inserter',
                'position': {'x': machine.global_position['x'] - 1, 'y': machine.global_position['y'] + 4},
                'direction': Direction.EAST
            }))
        mbi=mixed_belt_input()
        mbi.translate(-7,3)
        g.entities.append(mbi)
        return g


if __name__ == '__main__':
    print(inserters)
    i = InputInfrastructure()
    b = Blueprint()
    b.entities.append(i.build(AssemblingMachinesGroup(entities=[{'name': 'assembling-machine-3'}]), 'copper-cable'))
    print(b.to_string())
