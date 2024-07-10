from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.prototypes import pump

from cargo_wagon_block_maker.train_head import TrainHead, REQUESTS_SETTER, LTN_REQUESTER_COMBINATOR


class TrainHeadOneLiquid(TrainHead):
    def __init__(self, *, liquids, **kwargs):
        super().__init__(**kwargs)
        self.liquids = liquids
    def build(self, *, blueprint: Blueprint, flows, **kwargs):
        result=super().build(blueprint=blueprint, flows=flows, **kwargs)
        blueprint.add_circuit_connection(
            'red',
            ('train_head','loading_pumps',0),
            ('train_head','substation'),
        )
        blueprint.add_circuit_connection(
            'red',
            ('train_head','substation'),
            ('train_head','logistic-train-stop', 'output'),
        )
        blueprint.add_circuit_connection(
            'red',
            ('train_head','tanks',0),
            ('train_head',LTN_REQUESTER_COMBINATOR,REQUESTS_SETTER),
        )
        return result
    def create_pumps(self, line_loading_inserters):
        selected_entities=line_loading_inserters.entities[:1]
        g = self._create_pumps(selected_entities)
        return g

    def _create_pumps(self, selected_entities):
        g = Group(
            id="loading_pumps",
            entities=[
                {
                    "name": "pump",
                    "position": {
                        "x": ins.global_position["x"],
                        "y": ins.global_position["y"] - 6,
                    },
                    "control_behavior": {
                        "circuit_condition": {
                            "first_signal": {
                                "type": "fluid",
                                "name": liquid,
                            },
                            "constant": 0,
                            "comparator": ">",
                        },
                    }
                }
                for ins, liquid in zip(selected_entities, self.liquids)
            ],
        )
        return g
    def create_tanks(self, pumps):
        pump= pumps.entities[0]
        g = Group(
            id="tanks",
            entities=[
                {
                    "name": "storage-tank",
                    "position": {
                        "x": pump.global_position["x"]-2,
                        "y": pump.global_position["y"] - 1,
                    },
                    "direction": 2,
                }
            ],
        )
        return g

    def output(self, line_loading_inserters):
        result= super().output(line_loading_inserters)
        for r in result:
            r.entities= r.entities[1:]
        pumps= self.create_pumps(line_loading_inserters)
        tanks=self.create_tanks(pumps)
        pipes=self.create_pipes(pumps)
        result.append(pumps)
        result.append(tanks)
        result.append(pipes)
        return result

    def create_pipes(self, pumps):
        pump= pumps.entities[0]
        g = Group(
            id="pipes",
            entities=[
                {
                    "name": "pipe",
                    "position": {
                        "x": pump.global_position["x"],
                        "y": pump.global_position["y"] - 2
                    },
                }
            ],
        )
        return g



