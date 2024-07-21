from collections import Counter
from typing import List, Dict

from production_site import ProductionSite


class ProductionLine:
    def __init__(self, status, production_sites: Dict[str, ProductionSite], net_production: Dict[str, float]):
        self.status = status
        self.production_sites = production_sites
        self.net_production = net_production

    @property
    def global_input(self):
        return {production_site.recipe.products[0].name: production_site.quantity for production_site in
                self.production_sites.values() if 'ltn' in production_site.recipe.name}

    @property
    def ltn_input(self) -> Dict[str, ProductionSite]:
        return {recipe_name: site for recipe_name, site in self.production_sites.items() if 'ltn' in recipe_name}

    @property
    def prod_sites(self) -> List[ProductionSite]:
        return [site for site in self.production_sites.values() if 'ltn' not in site.recipe.name]

    @property
    def building_counts(self):
        c = Counter()
        for site in self.prod_sites:
            c[site.building.name] += site.building_count
        return c

    @property
    def total_building_count(self):
        return sum(self.building_counts.values())

    def print(self, duration=1):
        if self.status != "Optimal":
            print("Production line is not optimal")
        else:
            print("Production Sites")
            for recipe_name, production_site in self.ltn_input.items():
                print(
                    f'{recipe_name}: {production_site.quantity * duration:.2f} x {production_site.building.name} (input)')

            for production_site in self.prod_sites:
                print(
                    f'{production_site.recipe.name}: {production_site.quantity:.2f} x {production_site.building.name} ({production_site.recipe.category})')

            print("Net Production:")
            for item, production in self.net_production.items():
                print(f'{item}:{production}*{duration:.2f}')

    def __repr__(self):
        return self.print(duration=60)
