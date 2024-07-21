from typing import List, Tuple

from building_resolver import BuildingResolver
from core_helmod_model import build_core_model, solve_model
from model_finalizer import ModelSpecialization
from production_line import ProductionLine
from production_site import ProductionSite
from recipe_provider import RecipeProvider


class ProductionLineBuilder:
    def __init__(self, recipe_provider, building_resolver: BuildingResolver, model_finalizer: ModelSpecialization):
        self.recipe_provider: RecipeProvider = recipe_provider
        self.building_resolver = building_resolver
        self.production_rates = {
            recipe.name: 1/ recipe.energy
            for recipe in self.recipe_provider.recipes
            if self.building_resolver(recipe)
               is not None  # Free recipes are not craftable
        }
        self.model_finalizer = model_finalizer

    def build(self)-> ProductionLine:
        core_model = build_core_model(self.recipe_provider.as_dataframe(), self.production_rates)
        finalized_model = self.model_finalizer.finalize(core_model)
        status, production_sites, production_exprs = solve_model(finalized_model)
        epsilon = 0.0001
        production_sites = {
            k: ProductionSite(
                recipe=self.recipe_provider.by_name(k),
                quantity=v.value(),
                building=self.building_resolver(self.recipe_provider.by_name(k)),
            )
            for k, v in production_sites.items()
            if (v.value() or 0) > epsilon
        }
        net_production = {
            k: v.value()
            for k, v in production_exprs.items()
            if (v.value() or 0) > epsilon
        }
        if not net_production and status == 'Optimal':
            raise AssertionError("Line is optimal but produces nothing, this should not happen. Last cause was not enough max_assemblers")
        return ProductionLine(status, production_sites, net_production)
