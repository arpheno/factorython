from draftsman.classes.blueprint import Blueprint
from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.data.entities import inserters
from draftsman.prototypes.electric_pole import ElectricPole

from cargo_wagon_block_maker.assembling_machines_group import AssemblingMachinesGroup
from cargo_wagon_block_maker.bbmm import BlueprintMakerModule


def interior_medium_power_poles():
    g = Group(entities=[
        {
            "name": "medium-electric-pole",
            "position": {
                "x": 1,
                "y": 2
            }
        },
        {
            "name": "medium-electric-pole",
            "position": {
                "x": 4,
                "y": 5
            }
        },
    ])
    return g


def exterior_medium_power_poles():
    g = Group(entities=[
        {
            "name": "medium-electric-pole",
            "position": {
                "x": 4,
                "y": -5
            }
        },
        {
            "name": "medium-electric-pole",
            "position": {
                "x": 0,
                "y": -5
            }
        },
        {
            "name": "medium-electric-pole",
            "position": {
                "x": 0,
                "y": 11
            }
        },
        {
            "name": "medium-electric-pole",
            "position": {
                "x": 4,
                "y": 11
            }
        },
    ])
    return g


class MediumPowerPoles(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        g = Group()
        for machine in assembling_machines.top_row[::3]:
            p = interior_medium_power_poles()
            p.translate(machine.global_position['x'], machine.global_position['y'])
            g.entities.append(p)
        for machine in assembling_machines.top_row[1::4]:
            p = exterior_medium_power_poles()
            p.translate(machine.global_position['x'], machine.global_position['y'])
            g.entities.append(p)
        return g


class Substations(BlueprintMakerModule):
    def build(self, assembling_machines: AssemblingMachinesGroup, output: str):
        g = Group()
        for machine in assembling_machines.bottom_row[::6]:
            sub = ElectricPole(
                name='substation',
                position={
                    'x': machine.global_position['x'] + 8,
                    'y': machine.global_position['y'] + 5
                }

            )
            g.entities.append(sub)
        for machine in assembling_machines.top_row[::6]:
            sub = ElectricPole(
                name='substation',
                position={
                    'x': machine.global_position['x'] + 8,
                    'y': machine.global_position['y'] - 4
                }

            )
            g.entities.append(sub)
        return g
