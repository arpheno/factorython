from draftsman.classes.blueprint import Blueprint
from draftsman.classes.entity import Entity
from draftsman.classes.group import Group
from draftsman.prototypes import pump
from draftsman.prototypes.pipe import Pipe
from draftsman.prototypes.storage_tank import StorageTank

from cargo_wagon_block_maker.train_head import TrainHead, LTN_REQUESTER_COMBINATOR, REQUESTS_SETTER
from cargo_wagon_block_maker.train_head_one_liquids import TrainHeadOneLiquid
from cargo_wagon_block_maker.train_head_two_liquid import TrainHeadTwoLiquids


class TrainHeadThreeLiquids(TrainHeadTwoLiquids):
    def build(self, *, blueprint: Blueprint, flows, **kwargs):
        result=super().build(blueprint=blueprint, flows=flows, **kwargs)
        blueprint.add_circuit_connection(
            'red',
            ('train_head','loading_pumps',2),
            ('train_head','substation'),
        )
        blueprint.add_circuit_connection(
            'red',
            ('train_head','tanks',2),
            ('train_head',LTN_REQUESTER_COMBINATOR,REQUESTS_SETTER),
        )

        return result
    def create_pumps(self, line_loading_inserters):
        selected_entities=[line_loading_inserters.entities[0], line_loading_inserters.entities[-1], line_loading_inserters.entities[2]]
        g = self._create_pumps(selected_entities)
        return g

    def create_tanks(self, pumps):
        g= super().create_tanks(pumps)
        pump= pumps.entities[2]
        g.entities.append(
                StorageTank(**{
                    "name": "storage-tank",
                    "position": {
                        "x": pump.global_position["x"]+1,
                        "y": pump.global_position["y"]-3,
                    },
                    "direction": 2,
                }))
        return g
    def output(self, line_loading_inserters):
        result= super(TrainHeadOneLiquid, self).output(line_loading_inserters)
        for r in result:
            r.entities= []
        pumps= self.create_pumps(line_loading_inserters)
        tanks=self.create_tanks(pumps)
        pipes=self.create_pipes(pumps)
        result.append(pumps)
        result.append(tanks)
        result.append(pipes)
        return result

