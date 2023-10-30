from draftsman.classes.group import Group
from draftsman.prototypes.beacon import Beacon

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule


class Beacons(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup,**kwargs):
        g = Group()
        for top_ref in assembling_machines.top_row[2::4]:
            g.entities.append(
            Beacon(**{'name': 'beacon',
                      'position':{'x':top_ref.global_position['x']-1,
                                  'y':top_ref.global_position['y']-5},
                      'items': {'speed-module-2':8},
                      }))
        for bot_ref in assembling_machines.bottom_row[2::4]:
            g.entities.append(
            Beacon(**{'name': 'beacon',
                      'position':{'x':bot_ref.global_position['x']-1,
                                  'y':bot_ref.global_position['y']+4},
                      'items': {'speed-module-2':8},
                      }))
        return g