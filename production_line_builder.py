from model_builder import optimize_transformations


class ProductionLineBuilder:
    def __init__(self, recipe_provider, building_resolver):
        self.recipe_provider = recipe_provider
        self.building_resolver = building_resolver

    def build(self, product, quantity):
        recipes_df = self.recipe_provider.as_dataframe()
        production_rates = {
            recipe.name: self.building_resolver(recipe).crafting_speed / recipe.energy
            for recipe in self.recipe_provider.recipes
            if self.building_resolver(recipe) is not None  # Some recipes are not craftable?
        }
        status, optimal_quantities, production_exprs = optimize_transformations(
            recipes_df, production_rates, product, quantity
        )
        return status, optimal_quantities, production_exprs
