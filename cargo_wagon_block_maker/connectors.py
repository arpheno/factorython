import random
import warnings
from itertools import product, chain

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.filter_connector import filter_connector_4, filter_connector, flow_connector


def counter_combinator(flow):
    bp = '0eNrNVNtugzAM/Rc/TmmlUFpafmWaUAC3tQQJyqVaVfHvS4jG2rGK9mHaXpAS28fHJ8dcoGwcdpqkhfwCVClpIH+9gKGDFE24s+cOIQey2AIDKdpwEprssUVL1aJSbUlSWKWhZ0CyxnfIef/GAKUlSxgBh8O5kK4tUfuEGSgGnTK+WsnAwSOuss1yzeAMecbXvpFnarVqihKP4kS+wqd9QRU+XA/lJgT2pI0tJjOdSFvnb0YuMWOBojqGYQwGmIBlrAgKLTxt1aEWkRi8+FLlbOeeBu/jCBKrkWQSPgeNKK8Foxry1OeSrhzZ4ejFDfUTTZOx1SfjGUWzUdF0eU/TPTUW9UOmODTCGBhwXFCLc35tiOnE/NGJkzsTr5530e7GRTXpyCe2/AtP/WtLpc8LvP37Nf1NSQfPaqznHct+Vp5/T2Q34dXU+Sy+43xTfrdpXCAfHTY2v/rrMzj59R6ESrY8zXZJlm1SniXbvv8AUdYZOg=='
    block = Blueprint(bp)
    d = block.to_dict()
    k = Group()
    for entity in d['blueprint']['entities']:
        entity['entity_number'] -= 1
        k.entities.append(**{'name': entity['name'],
                             'position': entity['position'],
                             'control_behavior': entity['control_behavior']})
    for c, e in zip(d['blueprint']['entities'], k.entities):
        for number, value in c.get('connections', {}).items():
            for color, connections in value.items():
                for connection in connections:
                    print('adding', connection)
                    k.add_circuit_connection(color, e, connection['entity_id'] - 1, int(number),
                                             int(connection.get('circuit_id', 1)))
    k.translate(-k.entities[0].position['x'], -k.entities[0].position['y'])
    return k


def counting_connector():
    g = Group()
    for (x, y) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        g.entities.append(name='stack-filter-inserter', position={'x': x, 'y': y}, direction=Direction.WEST,
                          control_behavior= {'circuit_mode_of_operation': 1, 'circuit_read_hand_contents': True})
    # add circuit connections for red and green between all entities
    for i1, i2 in product(g.entities[::], g.entities[::]):
        g.add_circuit_connection('red', i1, i2)
        g.add_circuit_connection('green', i1, i2)
    return g


class Connectors(BlueprintMakerModule):
    def __init__(self, inserter_capacity_bonus_level=6, **kwargs):
        self.inserter_capacity_bonus_level = inserter_capacity_bonus_level
        self.stack_inserter = [(1 + x) * 2.31 for x in [1, 2, 3, 4, 6, 8, 10]]
        self.filter_inserter = [(x) * 2.31 for x in [1, 1, 2, 2, 2, 2, 3]]

    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        g = Group()
        for i,machine in enumerate(assembling_machines.top_row[1::2]):
            circuit = counter_combinator(0)
            circuit.id=f'circuit_{i}'
            circuit.translate(machine.global_position['x'], machine.global_position['y'] - 2)
            g.entities.append(circuit)
            connector = counting_connector()
            connector.id=f'connector_{i}'
            connector.translate(machine.global_position['x'] - 5, machine.global_position['y'] + 3)
            g.entities.append(connector)
        for i in range(len(g.entities)//2):
            g.add_circuit_connection('red',(f'circuit_{i}',0),(f'connector_{i}',0))
            g.add_circuit_connection('green',(f'circuit_{i}',1),(f'connector_{i}',0))
            try:
                g.add_circuit_connection('red',(f'circuit_{i}',2),(f'connector_{i+1}',0))
            except:
                pass # Index error but that's ok, we're at the end
        return g

    def nbuild(self, assembling_machines: AssemblingMachinesGroup, output: str):
        # We go through all blocks backwards, except first block
        g = Group()

        all_items_used = set()
        for block, flow in zip(assembling_machines.groups[::-1][:-1], assembling_machines.flows[::-1][:-1]):
            all_items_used.update(block.items_used)
            if any(f > self.stack_inserter[self.inserter_capacity_bonus_level] for f in flow.values()):
                warnings.warn(f"Flow of {flow} is too high for stack inserters")
            items_used = all_items_used
            if len(items_used) == 4:
                aiu = {item: "stack-filter-inserter" if 0 > flow.get(item, 0) > self.filter_inserter[
                    self.inserter_capacity_bonus_level] else "filter-inserter" for item in items_used}

                print("We can be smart about inserters")
                c = flow_connector(aiu.keys(), aiu.values())
            elif len(items_used - {output}) < 5:
                print("We can be smart about inserters, but need an output line")
                c = filter_connector_4(*(items_used - {output}))
            else:
                print("Damn, too many goods")
                choice = random.sample(items_used - {output}, 2)
                c = filter_connector(*choice)
            target = block[0].global_position['x'], 4
            c.translate(*target)
            g.entities.append(c)
        g.translate(-2, 0)
        return g
