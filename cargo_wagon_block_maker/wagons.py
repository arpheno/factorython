from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule

def wagon(filters):
    w = [
        {'name': 'cargo-wagon',
         'position': {'x': 0, 'y': 1},
         'orientation': 0.25,
         'inventory': {
             'filters': [{'index':i+1 , 'name': f} for i, f in enumerate(filters)],
                       'bar': len(filters)},
         },
        {'name': 'straight-rail',
         'position': {'x': -1, 'y': 1},
         'direction': Direction.EAST,
         },
        {'name': 'straight-rail',
         'position': {'x': 1, 'y': 1},
         'direction': Direction.EAST,
         }
    ]
    return Group(entities=w)
class Wagons(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        g = Group()
        for block in assembling_machines.groups:
            w=wagon(block.items_used)
            w.translate( block[0].global_position['x']+2, 4)
            g.entities.append(w)
        return g
if __name__ == '__main__':
    b=Blueprint()
    b.entities.append(wagon(['copper-cable']))
    print(b.to_string())