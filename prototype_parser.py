from collections import defaultdict

from prototype import Prototype


def parse_prototypes(prototypes: dict):
    prototypes = list(prototypes.values())
    prototypes = [Prototype(**p) for p in prototypes if "crafting_categories" in p if 'crafting_speed'in p]
    crafting_categories = defaultdict(list)
    for p in prototypes:
        for c in p.crafting_categories_list:
            crafting_categories[c].append(p)
    return crafting_categories
