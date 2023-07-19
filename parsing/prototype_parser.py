from collections import defaultdict

from data_structures.assembling_machine import AssemblingMachine


def parse_prototypes(assembly: dict):
    machines = [AssemblingMachine(**raw) for raw in assembly]

    crafting_categories = defaultdict(list)
    for p in machines:
        for c in p.crafting_categories:
            crafting_categories[c].append(p)
    return crafting_categories
