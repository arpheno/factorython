import random
import warnings
from itertools import product, chain

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.prototypes.arithmetic_combinator import ArithmeticCombinator
from draftsman.prototypes.constant_combinator import ConstantCombinator

from cargo_wagon_block_maker.bbmm import BlueprintMakerModule


signal_each = {"type": "virtual", "name": "signal-each"}


def arithmetic_combinator(
        *,
        position,
        direction,
        id=None,
        operation="*",
        first_signal=signal_each,
        output_signal=signal_each,
        second_constant=1,
):
    return ArithmeticCombinator(**{
        'name': 'arithmetic-combinator',
        'position': position,
        'direction': direction,
        'control_behavior': {
            "arithmetic_conditions": {
                "second_constant": second_constant,
                "operation": operation,
                "first_signal": first_signal,
                "output_signal": output_signal,
            }
        }
    })


def counting_combinator_without_bp(flow):
    g = Group()
    entities = {
        'constant': ConstantCombinator(position={'x': 0, 'y': 0}, direction=Direction.WEST),
        'minus_one': arithmetic_combinator(position={'x': 0, 'y': 3}, direction=Direction.WEST, operation='*',
                                           first_signal=signal_each, output_signal=signal_each, second_constant=-1),
        'plus_one': arithmetic_combinator(position={'x': 0, 'y': 2}, direction=Direction.WEST, operation='*',
                                          first_signal=signal_each, output_signal=signal_each, second_constant=1),
        'integrator': arithmetic_combinator(position={'x': 0, 'y': 1}, direction=Direction.WEST, operation='*',
                                            first_signal=signal_each, output_signal=signal_each, second_constant=1)
    }

    entities['constant'].signals = [# should be converted to constructor usage with control_behavior
        {"index": i + 1, "signal": {"type": "item", "name": item}, "count": flow[item]}
        for i, item in enumerate(flow )if not item in ['lubricant', 'sulfuric-acid','heavy-oil','water','petroleum-gas']
    ]
    for id, entity in entities.items():
        entity.id = id
        g.entities.append(entity)
    g.add_circuit_connection('green', 'constant','integrator', 1, 2)
    g.add_circuit_connection('red', 'integrator','integrator', 1, 2)
    g.add_circuit_connection('green', 'minus_one','integrator', 2, 1)
    g.add_circuit_connection('green', 'plus_one','integrator', 2, 1)
    return g




class Connectors(BlueprintMakerModule):
    def __init__(self, inserter_capacity_bonus_level=6,inserter_type='stack-filter-inserter', **kwargs):
        self.inserter_type = inserter_type
        self.inserter_capacity_bonus_level = inserter_capacity_bonus_level
        self.stack_inserter = [(1 + x) * 2.31 for x in [1, 2, 3, 4, 6, 8, 10]]
        self.filter_inserter = [(x) * 2.31 for x in [1, 1, 2, 2, 2, 2, 3]]

    def build(self, *, blueprint:Blueprint,**kwargs):
        assembling_machines=blueprint.entities['assembling_machines']
        g = Group()
        for i, (group, flow) in enumerate(
                zip(assembling_machines.groups, assembling_machines.flows)
        ):
            # sort machines by y position then x position
            group = sorted(
                group, key=lambda x: (x.global_position["y"], x.global_position["x"])
            )
            machine = group[0]
            circuit = counting_combinator_without_bp({k: 1 for k, v in flow.items() if v})
            circuit.id = f"circuit_{i}"
            circuit.translate(
                machine.global_position["x"]+(i%2)*4, machine.global_position["y"] - 6
            )
            g.entities.append(circuit)
            connector = self.counting_connector()
            connector.id = f"connector_{i}"
            connector.translate(
                machine.global_position["x"] - 2, machine.global_position["y"] + 3
            )
            g.entities.append(connector)
        for i in range(len(g.entities) // 2):
            g.add_circuit_connection("red", (f"circuit_{i}", 'minus_one'), (f"connector_{i}", 0))
            g.add_circuit_connection(
                "green", (f"circuit_{i}", 'integrator'), (f"connector_{i}", 0),2,1
            )
            try:
                g.add_circuit_connection(
                    "red", (f"circuit_{i}", 'plus_one'), (f"connector_{i + 1}", 0)
                )
            except:
                pass  # Index error but that's ok, we're at the end
        g.id='connectors'
        blueprint.entities.append(g)
        return g
    def counting_connector(self):
        g = Group()
        for (x, y) in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            g.entities.append(
                name= self.inserter_type if x==0  else  "filter-inserter",
                position={"x": x, "y": y},
                direction=Direction.WEST,
                control_behavior={
                    "circuit_mode_of_operation": 1,
                    "circuit_read_hand_contents": True,
                },
            )
        # add circuit connections for red and green between all entities
        for i1, i2 in product(g.entities[::], g.entities[::]):
            g.add_circuit_connection("red", i1, i2)
            g.add_circuit_connection("green", i1, i2)
        return g


if __name__ == '__main__':
    # give me a blueprint with arithmetic combinators
    counting_combinator_without_bp({'iron-plate': 1, 'copper-plate': 1, 'steel-plate': 1, 'plastic-bar': 1})
