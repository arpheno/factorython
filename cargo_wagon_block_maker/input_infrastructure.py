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
    def build(self,*,blueprint, **kwargs):
        assembling_machines=blueprint.entities['assembling_machines']
        g = self.connected_inserters(assembling_machines)
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
        # mbi = mixed_belt_input()
        # mbi.translate(-7, 3)
        # g.entities.append(mbi)
        g.id='input_infrastructure'
        blueprint.entities.append(g)
        for i, _ in enumerate(assembling_machines.groups):
            blueprint.add_circuit_connection('green', ('input_infrastructure', i, 0), ('connectors', f'circuit_{i}', 'plus_one'))
        return g

    def unconnected_inserters(self, assembling_machines):
        g = Group(entities=[input_inseter(machine) for machine in assembling_machines.entities])
        return g

    def connected_inserters(self, assembling_machines):
        G = Group()
        for group in assembling_machines.groups:
            sorted_group = sorted(group,key=lambda x: (x.global_position['y'],x.global_position['x']))
            offsets=[(0,2),(0,2),(1,-2),(-1,-2)]
            directions=[Direction.SOUTH,Direction.SOUTH,Direction.NORTH,Direction.NORTH]
            G.entities.append(Group(entities=[input_inseter(machine,offset,direction) for machine,offset,direction in zip(sorted_group,offsets,directions)]))
            for i1, i2 in zip(G.entities[-1].entities[::], G.entities[-1].entities[1::]):
                G.entities[-1].add_circuit_connection('green', i1, i2)
                G.entities[-1].add_circuit_connection('red', i1, i2)
        return G

def input_inseter(machine,inserter_offset,direction):
    return {
        "name": "fast-inserter",
        "position": {
            "x": machine.global_position["x"] +inserter_offset[0],
            "y": machine.global_position["y"] +inserter_offset[1]
        },
        'control_behavior':{'circuit_mode_of_operation': 3, 'circuit_read_hand_contents': True},
        "direction": direction
    }


if __name__ == '__main__':
    print(inserters)
    i = InputInfrastructure()
    b = Blueprint()
    b.entities.append(i.build(AssemblingMachinesGroup(entities=[{'name': 'assembling-machine-3'}]), 'copper-cable'))
    print(b.to_string())
