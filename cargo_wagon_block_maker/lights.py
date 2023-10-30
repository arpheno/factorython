from draftsman.classes.group import Group

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule

def lights():
    g=Group(entities=[
        {
            "name": "small-lamp",
            "position": {
                "x": 0,
                "y": -4
            }
        },
        {
            "name": "small-lamp",
            "position": {
                "x": 0,
                "y": 12
            }
        },
    ])
    return g

class Lights(BlueprintMakerModule):

    def build(self, assembling_machines: AssemblingMachinesGroup, **kwargs):
        g = Group()
        for machine in assembling_machines.top_row[1::4]:
            p = lights()
            p.translate(machine.global_position['x'], machine.global_position['y'])
            g.entities.append(p)
        return g
        pass
