from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import inserters
from draftsman.prototypes.inserter import Inserter

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.connectors import counting_combinator_without_bp
from cargo_wagon_block_maker.wagons import wagon


def stackinserters():
    entities = [
        {
            "name": "stack-inserter",
            "position": {"x": x, "y": y},
            "direction": Direction.WEST,
        }
        for x, y in [(0, 0), (0, 1), (1, 0), (1, 1)]
    ]
    g = Group(entities=entities)
    return g


class TrainHead(BlueprintMakerModule):
    def build(
            self, assembling_machines: AssemblingMachinesGroup, connectors: Group, flows, **kwargs
    ):
        g = Group()
        # Sort connectors by x position then y position

        probably_some_kind_of_combinator = min(
            connectors.entities,
            key=lambda x: (x.global_position["x"], x.global_position["y"]),
        )
        first_stack_filter_inserter = min(
            connectors.find_entities_filtered(name="stack-filter-inserter"),
            key=lambda x: (x.global_position["x"], x.global_position["y"]),
        )
        for i in range(3):
            w = wagon([])
            w.id = f"wagon_{i}"
            w.translate(
                probably_some_kind_of_combinator.global_position["x"] - 6 - i * 6, 4
            )
            g.entities.append(w)
        for i in range(2):
            inserters = stackinserters()
            inserters.id = f"stack_inserters_{i}"
            inserters.translate(
                probably_some_kind_of_combinator.global_position["x"] - 6 - 4 - i * 6, 4
            )
            g.entities.append(inserters)
        substation = {
            "name": "substation",
            "position": {
                "x": first_stack_filter_inserter.global_position["x"] - 7,
                "y": first_stack_filter_inserter.global_position["y"] - 7,
            },
        }
        left_stack_inserter_position = g.entities[
            ("stack_inserters_1", 0)
        ].global_position
        line_loading_inserters = Group(
            entities=[
                {
                    "name": "stack-inserter",
                    "position": {
                        "x": left_stack_inserter_position["x"] - 2 + i,
                        "y": left_stack_inserter_position["y"] - 1,
                    },
                    "control_behavior": {
                        "circuit_mode_of_operation": 1,
                        "circuit_read_hand_contents": True,
                    },
                }
                for i in range(6)
            ],
            id="line_loading_inserters",
        )
        for i in range(5):
            line_loading_inserters.add_circuit_connection("red", i, i + 1)
            line_loading_inserters.add_circuit_connection("green", i, i + 1)
        g.entities.append(line_loading_inserters)
        strongboxes = Group(
            id="strongboxes",
            entities=[
                {
                    "name": "aai-strongbox",
                    "position": {
                        "x": left_stack_inserter_position["x"] - 1 + i * 2,
                        "y": left_stack_inserter_position["y"] - 2,
                    },
                }
                for i in range(3)
            ],
        )
        for i in range(2):
            strongboxes.add_circuit_connection('red', i, i + 1)
        g.entities.append(strongboxes)
        unloading_inserters = Group(
            id="unloading_inserters",
            entities=[
                {
                    "name": "stack-inserter",
                    "position": {
                        "x": ins.global_position["x"],
                        "y": ins.global_position["y"] - 3,
                    },
                }
                for ins in line_loading_inserters.entities
            ],
        )
        g.entities.append(unloading_inserters)
        loading_inserters = Group(
            id="loading_inserters",
            entities=[
                {
                    "name": "stack-inserter",
                    "position": {
                        "x": ins.global_position["x"],
                        "y": ins.global_position["y"] - 6,
                    },
                }
                for ins in line_loading_inserters.entities
            ],
        )
        g.entities.append(loading_inserters)
        line_unloading_inserters = Group(
            id="line_unloading_inserters",
            entities=[
                {
                    "name": "fast-inserter",
                    "position": {
                        "x": ins.global_position["x"],
                        "y": ins.global_position["y"] - 8,
                    },
                }
                for ins in line_loading_inserters.entities
            ],
        )
        g.entities.append(line_unloading_inserters)
        buffer_chests = Group(
            id="buffer_chests",
            entities=[
                {
                    "name": "iron-chest",
                    "position": {
                        "x": ins.global_position["x"],
                        "y": ins.global_position["y"] - 7,
                    },
                }
                for ins in line_loading_inserters.entities
            ],
        )
        g.entities.append(buffer_chests)
        rails = Group(id='rails', entities=[
            {'name': 'straight-rail',
             'position': {'x': left_stack_inserter_position['x'] - 11 + i * 2,
                          'y': left_stack_inserter_position['y'] - 5},
             'direction': Direction.EAST,
             } for i in range(12)
        ])
        g.entities.append(rails)
        right_rail_position = rails.entities[-1].global_position
        train_stop = {'name': 'logistic-train-stop',
                      'position': {'x': right_rail_position['x'], 'y': right_rail_position['y'] + 2},
                      'direction': Direction.EAST}

        g.entities.append(**train_stop)

        leftmost_constant_combinator = min(connectors.find_entities_filtered(name='constant-combinator'),
                                           key=lambda x: x.global_position['x'])
        combinator = counting_combinator_without_bp({})
        combinator.id='circuit'
        new_const = combinator.find_entities_filtered(name='constant-combinator')[0]
        new_const.signals = leftmost_constant_combinator.signals
        combinator.translate(left_stack_inserter_position['x']+5,left_stack_inserter_position['y']-4)
        g.entities.append(combinator)

        g.entities.append(**substation)
        return g
