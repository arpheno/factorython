from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import inserters

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule


class InputInfrastructure(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        g = Group(entities=[

            # if the building is facing south, place the input infrastructure to the north
            {
                "name": "fast-inserter",
                "position": {
                    "x": machine.global_position["x"],
                    "y": machine.global_position["y"] - 2 if machine.direction == Direction.SOUTH else
                    machine.global_position["y"] + 2,
                },
                "direction": Direction.SOUTH
                if machine.direction == Direction.NORTH
                else Direction.NORTH,
            }
            for machine in assembling_machines.entities])
        return g


if __name__ == '__main__':
    i=InputInfrastructure()
    b=Blueprint()
    b.entities.append(i.build(AssemblingMachinesGroup(entities=[{'name':'assembling-machine-3'}]), 'copper-cable'))
    print(b.to_string())