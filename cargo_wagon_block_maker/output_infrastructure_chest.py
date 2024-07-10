from itertools import product

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.logistic_passive_container import LogisticPassiveContainer
from draftsman.prototypes.underground_belt import UndergroundBelt

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.belt import belt
from cargo_wagon_block_maker.output_infrastructure import OutputInfrastructure


class OutputInfrastructureChest(OutputInfrastructure):
    def output_destination(self, assembling_machines, g):
        inserters = g.entities[-1]
        # There's 8 groups of inserters in g
        # find the inserters that have maximum y and minimum y
        # These are the inserters that are the closest to the output
        all_entities = []
        for group in g.entities:
            all_entities.extend(group.entities)

        inserters = [entity for entity in all_entities if entity.name == 'inserter']
        # Add a chest to each inserter, keeping in mind the inserter's direction
        for inserter in inserters:
            chest = LogisticPassiveContainer(**{
                "position": {
                    "x": inserter.global_position["x"],
                    "y": inserter.global_position["y"] + 1 if inserter.direction == Direction.NORTH else
                    inserter.global_position["y"] - 1,
                },
            })
            g.entities.append(chest)
