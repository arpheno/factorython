from typing import List, Dict

from production_site import ProductionSite


class ProductionLine:
    def __init__(self, status, production_sites: Dict[str,ProductionSite], net_production:Dict[str,float]):
        self.status = status
        self.production_sites = production_sites
        self.net_production = net_production

    def print(self, ):

        if self.status != "Optimal":
            print("Production line is not optimal")
        else:
            print("Production Sites")
            for recipe_name,production_site in self.production_sites.items():
                print(f'{recipe_name}: {production_site.quantity:.2f} x {production_site.building.name}')

            print("Net Production:")
            for item, production in self.net_production.items():
                print(item, ":", production)
