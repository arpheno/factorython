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
    def build(self,*,blueprint,**kwargs):
        assembling_machines=blueprint.entities['assembling_machines']
        g = Group()
        all_items_used = set()
        for block in assembling_machines.groups[::-1]:
            all_items_used.update(block.items_used)
        for block in assembling_machines.groups[::-1]:
            w=wagon(all_items_used-{'lubricant','sulfuric-acid','water','rgspm','rgbspm','rgbospm'})
            w.translate( block[0].global_position['x']+2, 4)
            g.entities.append(w)
        g.id='wagons'
        blueprint.entities.append(g)
        return g
if __name__ == '__main__':
    b=Blueprint()
    b.entities.append(wagon(['copper-cable']))
    print(b.to_string())