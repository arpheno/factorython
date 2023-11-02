from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import inserters
from draftsman.prototypes.inserter import Inserter

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.connectors import counting_combinator_without_bp
from cargo_wagon_block_maker.wagons import wagon

LTN_SIGNALS = 'ltn-signals'

STRONGBOXES = "strongboxes"

LTN_REQUESTER_COMBINATOR = "ltn_requester_combinator"

NEGATIVE_LIMITER = "negative_limiter"

REQUESTS_SETTER = 'requests_setter'


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
    def build(self, *, blueprint: Blueprint, flows, **kwargs):
        connectors = blueprint.entities["connectors"]
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
                    "name": "stack-filter-inserter",
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
            id=STRONGBOXES,
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
            strongboxes.add_circuit_connection("red", i, i + 1)
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
        ref_x = left_stack_inserter_position["x"] - 11
        ref_y = left_stack_inserter_position["y"] - 5
        rails = Group(
            id="rails",
            entities=[
                         {
                             "name": "straight-rail",
                             "position": {
                                 "x": left_stack_inserter_position["x"] - 11 + i * 2,
                                 "y": left_stack_inserter_position["y"] - 5,
                             },
                             "direction": Direction.EAST,
                         }
                         for i in range(12)
                     ] +
                     [{'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -20.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -18.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -16.0}},
                      {'name': 'curved-rail', 'position': {'x': ref_x + -67.0, 'y': ref_y + -13.0},
                       'direction': Direction.SOUTH},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -14.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -12.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -10.0}},
                      {'name': 'rail-chain-signal', 'position': {'x': ref_x + -66.5, 'y': ref_y + -9.5},
                       'direction': Direction.NORTHWEST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -64.0, 'y': ref_y + -10.0},
                       'direction': Direction.SOUTHWEST},
                      {'name': 'curved-rail', 'position': {'x': ref_x + -61.0, 'y': ref_y + -7.0},
                       'direction': Direction.NORTHWEST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -8.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -6.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -56.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -54.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -52.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -50.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -48.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -46.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -44.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -42.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -40.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -38.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -36.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -34.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -32.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -30.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -28.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -26.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -24.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -22.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -20.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -18.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -16.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -14.0, 'y': ref_y + -6.0},
                       'direction': Direction.EAST},
                      {'name': 'curved-rail', 'position': {'x': ref_x + -9.0, 'y': ref_y + -5.0},
                       'direction': Direction.SOUTHEAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -4.0}},
                      {'name': 'rail-signal', 'position': {'x': ref_x + -48.5, 'y': ref_y + -4.5},
                       'direction': Direction.WEST},
                      {'name': 'rail-signal', 'position': {'x': ref_x + -26.5, 'y': ref_y + -4.5},
                       'direction': Direction.WEST},
                      {'name': 'curved-rail', 'position': {'x': ref_x + -3.0, 'y': ref_y + -1.0},
                       'direction': Direction.NORTHWEST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + -2.0}},
                      {'name': 'rail-chain-signal', 'position': {'x': ref_x + -50.5, 'y': ref_y + -1.5},
                       'direction': Direction.EAST},
                      {'name': 'rail-signal', 'position': {'x': ref_x + -28.5, 'y': ref_y + -1.5},
                       'direction': Direction.EAST},
                      {'name': 'rail-signal', 'position': {'x': ref_x + -7.5, 'y': ref_y + -2.5},
                       'direction': Direction.NORTHWEST},
                      {'name': 'rail-signal', 'position': {'x': ref_x + -6.5, 'y': ref_y + -1.5},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 0.0}},
                      {'name': 'curved-rail', 'position': {'x': ref_x + -61.0, 'y': ref_y + 1.0},
                       'direction': Direction.WEST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -56.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -54.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -52.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -50.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -48.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -46.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -44.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -42.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -40.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -38.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -36.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -34.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -32.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -30.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -28.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -26.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -24.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -22.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -20.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -18.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -16.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -14.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -12.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -10.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -8.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -6.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -4.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -2.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + 0.0, 'y': ref_y + 0.0},
                       'direction': Direction.EAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 2.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -64.0, 'y': ref_y + 4.0},
                       'direction': Direction.NORTHWEST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 4.0}},
                      {'name': 'curved-rail', 'position': {'x': ref_x + -67.0, 'y': ref_y + 7.0},
                       'direction': Direction.NORTHEAST},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 6.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 8.0}},
                      {'name': 'rail-signal', 'position': {'x': ref_x + -69.5, 'y': ref_y + 10.5}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 10.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 12.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 14.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 16.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 18.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 20.0}},
                      {'name': 'straight-rail', 'position': {'x': ref_x + -68.0, 'y': ref_y + 22.0}}]
        )
        g.entities.append(rails)
        right_rail_position = max(rails.find_entities_filtered(name='straight-rail'),key=lambda x: x.global_position['x']).global_position
        train_stop = {
            "name": "logistic-train-stop",
            "position": {
                "x": right_rail_position["x"],
                "y": right_rail_position["y"] + 2,
            },
            "direction": Direction.EAST,
        }
        train_stop_input = {
            "name": "logistic-train-stop-input",
            "id": "input",
            "position": {
                "x": right_rail_position["x"] + 0.5,
                "y": right_rail_position["y"] + 0.5 + 2,
            },
        }
        logistic_train_stop = Group(
            entities=[train_stop, train_stop_input], id="logistic-train-stop"
        )
        g.entities.append(logistic_train_stop)

        leftmost_constant_combinator = min(
            connectors.find_entities_filtered(name="constant-combinator"),
            key=lambda x: x.global_position["x"],
        )
        combinator = counting_combinator_without_bp({})
        combinator.id = "circuit"
        new_const = combinator.find_entities_filtered(name="constant-combinator")[0]
        new_const.signals = leftmost_constant_combinator.signals
        combinator.translate(
            left_stack_inserter_position["x"] + 5, left_stack_inserter_position["y"] - 4
        )
        g.entities.append(combinator)
        # This should go somewhere else,
        total_stacks = 96 * 3
        stack_sizes = {
            "coal": 50,
            "stone": 50,
            "iron-ore": 50,
            "copper-ore": 50,
        }
        operating_time = 60
        needs = {
            item: needs_per_second * operating_time
            for item, needs_per_second in flows[0].items()
            if needs_per_second > 0
        }
        minimum_stacks = 40
        stacks_needed = {
            item: max(need / stack_sizes.get(item, 100), minimum_stacks)
            for item, need in needs.items()
        }
        items_needed = {
            item: stacks_needed[item] * stack_sizes.get(item, 100)
            for item in stacks_needed
        }
        ltn_requester_combinator = Group(
            entities=[
                {
                    "name": "constant-combinator",
                    "id": REQUESTS_SETTER,
                    "position": {
                        "x": new_const.global_position["x"] + 1,
                        "y": new_const.global_position["y"],
                    },
                    'control_behavior': {'filters': [
                        {
                            "index": i + 1,
                            "count": -items_needed[item],
                            "signal": {"type": "item", "name": item},
                        }
                        for i, item in enumerate(items_needed)
                    ]}
                },
                {
                    "name": "decider-combinator",
                    "id": NEGATIVE_LIMITER,
                    "position": {
                        "x": new_const.global_position["x"] + 3,
                        "y": new_const.global_position["y"],
                    },
                    "direction": Direction.EAST,
                    "control_behavior": {
                        "decider_conditions": {
                            "constant": 0,
                            "comparator": "<",
                            "copy_count_from_input": True,
                            "first_signal": {"type": "virtual", "name": "signal-each"},
                            "output_signal": {"type": "virtual", "name": "signal-each"},
                        }
                    },
                },
                {
                    "name": "constant-combinator",
                    "id": LTN_SIGNALS,
                    "position": {
                        "x": new_const.global_position["x"] + 4,
                        "y": new_const.global_position["y"],
                    },
                    'control_behavior': {
                        'filters': [{'count': 3, 'index': 1, 'signal': {'type': 'virtual', 'name': 'ltn-max-trains'}},
                                    {'count': 3, 'index': 2,
                                     'signal': {'type': 'virtual', 'name': 'ltn-max-train-length'}},
                                    {'count': 3, 'index': 3,
                                     'signal': {'type': 'virtual', 'name': 'ltn-min-train-length'}},
                                    {'count': 30, 'index': 4,
                                     'signal': {'type': 'virtual', 'name': 'ltn-requester-stack-threshold'}},
                                    {'count': 1, 'index': 5,
                                     'signal': {'type': 'virtual', 'name': 'ltn-requester-priority'}}]}
                },
            ],
            id=LTN_REQUESTER_COMBINATOR,
        )
        g.entities.append(ltn_requester_combinator)
        g.entities.append(**substation)
        g.id = "train_head"
        g.add_circuit_connection(
            "red", ("line_loading_inserters", 5), (f"circuit", "minus_one")
        )
        g.add_circuit_connection(
            "green", ("line_loading_inserters", 5), (f"circuit", "integrator"), 1, 2
        )
        g.add_circuit_connection(
            "red",
            (STRONGBOXES, 2),
            (LTN_REQUESTER_COMBINATOR, REQUESTS_SETTER),
        )
        g.add_circuit_connection(
            "red",
            (LTN_REQUESTER_COMBINATOR, NEGATIVE_LIMITER),
            (LTN_REQUESTER_COMBINATOR, REQUESTS_SETTER),
        )
        g.add_circuit_connection(
            "red",
            (LTN_REQUESTER_COMBINATOR, NEGATIVE_LIMITER),
            ("logistic-train-stop", "input"),
            2,
            1,
        )
        g.add_circuit_connection(
            "red",
            (LTN_REQUESTER_COMBINATOR, LTN_SIGNALS),
            ("logistic-train-stop", "input"),
        )
        blueprint.entities.append(g)
        blueprint.add_circuit_connection(
            "red",
            ("train_head", "circuit", "plus_one"),
            ("connectors", "connector_0", 0),
        )
        return g
