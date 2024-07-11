from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import inserters
from draftsman.prototypes.inserter import Inserter

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.connectors import counting_combinator_without_bp
from cargo_wagon_block_maker.wagons import wagon

stack_sizes = {
    "coal": 50,
    "stone": 50,
    "iron-ore": 50,
    "copper-ore": 50,
}
LIQUIDS = ["water", "sulfuric-acid", "lubricant", "petroleum-gas", "light-oil", "heavy-oil", "crude-oil", "steam"]
LTN_SIGNALS = 'ltn-signals'
STRONGBOXES = "strongboxes"
LTN_REQUESTER_COMBINATOR = "ltn_requester_combinator"
NEGATIVE_LIMITER = "negative_limiter"
REQUESTS_SETTER = 'requests_setter'


def stackinserters(name="stack-inserter"):
    entities = [
        {
            "name": name,
            "position": {"x": x, "y": y},
            "direction": Direction.WEST,
        }
        for x, y in [(0, 0), (0, 1), (1, 0), (1, 1)]
    ]
    g = Group(entities=entities)
    return g


class TrainHead(BlueprintMakerModule):
    def __init__(self,operating_time=60,minimum_stacks=40,inserter_type='stack-filter-inserter',**kwargs):
        self.operating_time = operating_time
        self.minimum_stacks = minimum_stacks
        self.inserter_type = inserter_type


    def build(self, *, blueprint: Blueprint, flows, **kwargs):


        items_needed = self.calculate_needs(flows)
        connectors = blueprint.entities["connectors"]
        g = Group()

        probably_some_kind_of_combinator = min(
            connectors.entities,
            key=lambda x: (x.global_position["x"], x.global_position["y"]),
        )
        first_stack_filter_inserter = min(
            connectors.find_entities_filtered(name=self.inserter_type),
            key=lambda x: (x.global_position["x"], x.global_position["y"]),
        )
        wagons = self.create_wagons(probably_some_kind_of_combinator)
        g.entities.extend(wagons)

        for i in range(2):
            inserters = stackinserters()
            inserters.id = f"stack_inserters_{i}"
            inserters.translate(
                probably_some_kind_of_combinator.global_position["x"] - 6 - 4 - i * 6, 4
            )
            g.entities.append(inserters)
        left_stack_inserter_position = g.entities[("stack_inserters_1", 0)].global_position # Grab the leftmost stack inserter as a reference point
        line_loading_inserters = self.create_line_loading_inserters(left_stack_inserter_position)
        for i in range(5):
            line_loading_inserters.add_circuit_connection("red", i, i + 1)
            line_loading_inserters.add_circuit_connection("green", i, i + 1)
        g.entities.append(line_loading_inserters)
        strongboxes = self.create_strongboxes(left_stack_inserter_position)
        g.entities.append(strongboxes)
        train_unloading_inserters = self.create_train_unloading_inserters(line_loading_inserters)
        # Output
        output=self.output(line_loading_inserters)
        g.entities.extend(output)
        g.entities.append(train_unloading_inserters)
        ref_x = left_stack_inserter_position["x"] - 11
        ref_y = left_stack_inserter_position["y"] - 5
        rails = self.create_rails(left_stack_inserter_position, ref_x, ref_y)
        g.entities.append(rails)
        g.entities.append( self.create_logistic_train_stop(rails))

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
        ltn_requester_combinator = self.create_ltn_requester_combinator(items_needed, new_const)

        g.entities.append(ltn_requester_combinator)
        g.entities.append(**self.create_substation_next_to_trainstation(first_stack_filter_inserter))
        g.id = "train_head"
        g.add_circuit_connection(
            'red',
            ( 'substation'),
            ( 'logistic-train-stop', 'output'),
        )
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

    def output(self, line_loading_inserters):
        result = []
        result.append(self.create_train_loading_inserters(line_loading_inserters))
        result.append(self.create_belt_output_inserters(line_loading_inserters))
        result.append(self.create_buffer_chests(line_loading_inserters))
        return result

    def create_buffer_chests(self, line_loading_inserters):
        return Group(
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

    def create_rails(self, left_stack_inserter_position, ref_x, ref_y):
        return Group(
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

    def create_logistic_train_stop(self, rails):
        right_rail_position = max(rails.find_entities_filtered(name='straight-rail'),
                                  key=lambda x: x.global_position['x']).global_position
        train_stop = {
            "name": "logistic-train-stop",
            'id':'output',
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
        return logistic_train_stop

    def calculate_needs(self, flows):
        needs = {
            item: needs_per_second * self.operating_time
            for item, needs_per_second in flows[0].items()
            if needs_per_second > 0
        }
        stacks_needed = {
            item: max(need / stack_sizes.get(item, 100), self.minimum_stacks)
            for item, need in needs.items()
        }
        items_needed = {
            item: stacks_needed[item] * stack_sizes.get(item, 100)
            for item in stacks_needed
        }
        return items_needed

    def create_ltn_requester_combinator(self, items_needed, new_const):
        return Group(
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
                            "count": -int(items_needed[item]),
                            "signal": {"type": "item" if item not in LIQUIDS else "fluid", "name": item},
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

    def create_substation_next_to_trainstation(self, first_stack_filter_inserter):
        substation = {
            "name": "substation",
            'id': 'substation',
            "position": {
                "x": first_stack_filter_inserter.global_position["x"] - 7,
                "y": first_stack_filter_inserter.global_position["y"] - 7,
            },
        }
        return substation

    def create_line_loading_inserters(self, left_stack_inserter_position):
        return Group(
            entities=[
                {
                    "name": self.inserter_type,
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

    def create_strongboxes(self, left_stack_inserter_position):
        g=Group(
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
            g.add_circuit_connection("red", i, i + 1)
        return g

    def create_train_unloading_inserters(self, line_loading_inserters):
        return Group(
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

    def create_train_loading_inserters(self, line_loading_inserters):
        """ These are the inserters that load from outut chests to the train"""
        return Group(
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

    def create_belt_output_inserters(self, line_loading_inserters):
        """ These are the inserters that put shit from the belt into the train loading chests for output"""
        return Group(
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

    def create_wagons(self, probably_some_kind_of_combinator):
        wagons = []
        for i in range(3):
            w = wagon([])
            w.id = f"wagon_{i}"
            w.entities[0].inventory['bar'] = 25
            w.translate(
                probably_some_kind_of_combinator.global_position["x"] - 6 - i * 6, 4
            )
            wagons.append(w)
        return wagons
