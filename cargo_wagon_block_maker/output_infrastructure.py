from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import inserters, transport_belts
from draftsman.prototypes.inserter import Inserter
from draftsman.prototypes.transport_belt import TransportBelt

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule

def undergrounds():
    g=Group(entities=[
        {
            "name": "underground-belt",
            "position": {
                "x": 0,
                "y": 3
            },
            "direction": Direction.EAST,
            "type": "input"
        },
        {
            "name": "underground-belt",
            "position": {
                "x": 4,
                "y": 3
            },
            "direction": Direction.EAST,
            "type": "output"
        },
    ])
    return g
class OutputInfrastructure(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        g = Group(entities=[ {
                "name": "fast-inserter",
                "position": {
                    "x": machine.global_position["x"],
                    "y": machine.global_position["y"] - 2
                },
                "direction": Direction.SOUTH
            }for machine in assembling_machines.top_row])
        mapping = {2:1}
        for i,machine in enumerate(assembling_machines.bottom_row):
            if not machine.recipe==output:
                continue
            i= Inserter(**
                {
                    "name": "fast-inserter",
                    "direction": Direction.NORTH,
                    "position": {
                        "x": machine.global_position["x"]+mapping.get(i%4,0),
                        "y": machine.global_position["y"]+2,
                    },
                })
            g.entities.append(i)

        #Lower belt
        for machine in assembling_machines.bottom_row[1::4]:
            p = undergrounds()
            p.translate(machine.global_position['x'], machine.global_position['y'])
            g.entities.append(p)
        u=sorted([e.global_position['x'] for e in g.find_entities_filtered(name='underground-belt')])
        u.insert(0,assembling_machines.bottom_row[0].global_position['x']-1)
        u.append(assembling_machines.bottom_row[-1].global_position['x']+2)
        for source,destination in zip(u[::2],u[1::2]):
            for x in range(int(source+1),int(destination)):
                g.entities.append(TransportBelt(**{
                    "name": "transport-belt",
                    "position": {
                        "x": x,
                        "y": assembling_machines.bottom_row[0].global_position['y']+3
                    },
                    "direction": Direction.EAST,
                }))
        u=[]
        u.insert(0,assembling_machines.top_row[0].global_position['x']-1)
        u.append(assembling_machines.top_row[-1].global_position['x']+2)
        for source,destination in zip(u[::2],u[1::2]):
            for x in range(int(source+1),int(destination)):
                g.entities.append(TransportBelt(**{
                    "name": "transport-belt",
                    "position": {
                        "x": x,
                        "y": assembling_machines.top_row[0].global_position['y']-3
                    },
                    "direction": Direction.EAST,
                }))
        return g
if __name__ == '__main__':
    print(transport_belts)