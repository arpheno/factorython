from draftsman.classes.group import Group
from draftsman.prototypes.roboport import Roboport

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule


class Roboports(BlueprintMakerModule):
    def build(self,blueprint, **kwargs):
        g = Group()
        assembling_machines=blueprint.entities['assembling_machines']
        top_ref=assembling_machines.top_row[3]
        g.entities.append(
        Roboport(**{'name': 'roboport',
                  'position':{'x':top_ref.global_position['x']+8,
                              'y':top_ref.global_position['y']-4},
                  'items': {'speed-module-2':8},
                     }))
        g.id='roboports'
        blueprint.entities.append(g)
        return g