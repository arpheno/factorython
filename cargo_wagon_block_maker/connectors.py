import random
import warnings

from draftsman.classes.group import Group

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.filter_connector import filter_connector_4, filter_connector, flow_connector


class Connectors(BlueprintMakerModule):
    def __init__(self, inserter_capacity_bonus_level=6, **kwargs):
        self.inserter_capacity_bonus_level = inserter_capacity_bonus_level
        self.stack_inserter = [(1 + x) * 2.31 for x in [1, 2, 3, 4, 6, 8, 10]]
        self.filter_inserter = [(x) * 2.31 for x in [1, 1, 2, 2, 2, 2, 3]]

    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        # We go through all blocks backwards, except first block
        g = Group()

        all_items_used = set()
        for block, flow in zip(assembling_machines.groups[::-1][:-1], assembling_machines.flows[::-1][:-1]):
            all_items_used.update(block.items_used)
            if any(f > self.stack_inserter[self.inserter_capacity_bonus_level] for f in flow.values()):
                warnings.warn(f"Flow of {flow} is too high for stack inserters")
            items_used = all_items_used
            if len(items_used) == 4:
                aiu = {item: "stack-filter-inserter" if 0>flow.get(item,0) > self.filter_inserter[
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
