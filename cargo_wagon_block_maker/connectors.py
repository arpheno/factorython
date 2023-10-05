import random

from draftsman.classes.group import Group

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule
from cargo_wagon_block_maker.filter_connector import filter_connector_4, filter_connector


class Connectors(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        # We go through all blocks backwards, except first block
        g = Group()

        all_items_used = set()
        for block in assembling_machines.groups[::-1][:-1]:
            all_items_used.update(block.items_used)
            items_used = all_items_used
            if len(items_used) == 4:
                print("We can be smart about inserters")
                c = filter_connector_4(*items_used)
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
        g.translate(-2,0)
        return g
