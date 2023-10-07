from itertools import product

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.underground_belt import UndergroundBelt

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.belt import belt


def undergrounds():
    g = Group(entities=[
        {
            "name": "underground-belt",
            "position": {
                "x": -1,
                "y": 3
            },
            "direction": Direction.WEST,
            "type": "output"
        },
        {
            "name": "underground-belt",
            "position": {
                "x": 4,
                "y": 3
            },
            "direction": Direction.WEST,
            "type": "input"
        },
        {'name': 'underground-belt',
         'position': {'x': -2, 'y': 3},
         'direction': Direction.WEST,
         'type': 'input'
         },
        {'name': 'underground-belt',
         'position': {'x': 5, 'y': 3},
         'direction': Direction.WEST,
         'type': 'output'
         },
    ])
    return g


class OutputInfrastructure(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        self.output=output
        g = Group()
        for group in assembling_machines.groups:
            #Sort the group by y position then x position
            group=sorted(group,key=lambda x: (x.global_position['y'], x.global_position['x']))
            g.entities.append(Group(entities=[
                self.inserter(machine,i) for i,machine in enumerate(group)
            ]))
            for i1, i2 in product(g.entities[-1].entities[::], g.entities[-1].entities[::]):
                g.entities[-1].add_circuit_connection('red', i1, i2)
                g.entities[-1].add_circuit_connection('green', i1, i2)
        # Lower belt
        for machine in assembling_machines.bottom_row[1::4]:
            p = undergrounds()
            p.translate(machine.global_position['x'], machine.global_position['y'])
            g.entities.append(p)
        # Upper belt
        for machine in assembling_machines.top_row[1::4]:
            p = undergrounds()
            p.translate(machine.global_position['x'], machine.global_position['y'])
            p.translate(0, -6)  # To offset it from below the machine to above
            g.entities.append(p)
        # upper output
        underground = UndergroundBelt(**{
            "name": "underground-belt",
            "position": {
                "x": assembling_machines.top_row[0].global_position['x'] - 3,
                "y": assembling_machines.top_row[0].global_position['y'] - 3,
            },
            "direction": Direction.WEST,
            "type": "output"
        })
        g.entities.append(underground)
        b = belt((underground.global_position['x'] - 1, underground.global_position['y']),
                 (underground.global_position['x'] - 1, underground.global_position['y'] + 4))
        g.entities.append(b)
        #crossing
        underground = UndergroundBelt(**{
            "name": "underground-belt",
            "position": {
                "x": assembling_machines.top_row[0].global_position['x'] - 4,
                "y": assembling_machines.top_row[0].global_position['y'] + 1,
            },
            "direction": Direction.SOUTH,
            "type": "input"
        })
        g.entities.append(underground)
        # lower output
        underground = UndergroundBelt(**{
            "name": "underground-belt",
            "position": {
                "x": assembling_machines.bottom_row[0].global_position['x'] - 3,
                "y": assembling_machines.bottom_row[0].global_position['y'] + 3,
            },
            "direction": Direction.WEST,
            "type": "output"
        })

        p = belt((underground.global_position['x'] , underground.global_position['y']),
                 (underground.global_position['x'] - 4, underground.global_position['y']))
        b = belt((underground.global_position['x'] - 1, underground.global_position['y'] - 3),
                 (underground.global_position['x'] - 1, underground.global_position['y']))
        g.entities.append(p)
        g.entities.append(underground)
        g.entities.append(b)
        #crossing
        crossing = UndergroundBelt(**{
            "name": "underground-belt",
            "position": {
                "x": assembling_machines.bottom_row[0].global_position['x'] -4 ,
                "y": assembling_machines.bottom_row[0].global_position['y'] - 1,
            },
            "direction": Direction.SOUTH,
            "type": "output"
        })
        g.entities.append(crossing)
        # Little output belt to the left
        return g

    def inserter(self, machine,i):
        mapping = {0: 1, 2: 1, 1: -1, 3: -1}
        if not machine.recipe == self.output:
            i = Inserter(**
                         {
                             "name": "fast-inserter",
                             "position": {
                                 "x": machine.global_position["x"],
                                 "y": machine.global_position["y"] + 2 if machine.direction == Direction.NORTH else
                                 machine.global_position["y"] - 2,
                             },
                             'control_behavior':{'circuit_mode_of_operation': 3, 'circuit_read_hand_contents': True},
                             "direction": Direction.SOUTH
                             if machine.direction == Direction.SOUTH
                             else Direction.NORTH,

                         })
        else:
            i = Inserter(**
                         {
                             "name": "inserter",
                             "direction": Direction.NORTH if machine.direction == Direction.SOUTH else Direction.SOUTH,
                             'control_behavior':{'circuit_mode_of_operation': 3, 'circuit_read_hand_contents': True},
                             "position": {
                                 "x": machine.global_position["x"] + mapping[i],
                                 "y": machine.global_position["y"] + 2 if machine.direction == Direction.SOUTH else -1,
                             },
                         })
        return i


if __name__ == '__main__':
    b = Blueprint()
    b.entities.append(belt((0, 0), (10, 0)))
    b.entities.append(belt((0, 0), (0, 10)))
    b.entities.append(belt((0, 10), (10, 10)))
    b.entities.append(belt((10, 0), (10, 10)))
    print(b.to_string())
