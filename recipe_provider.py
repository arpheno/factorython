import pandas as pd

from data_structures.recipe import Recipe, Product


class RecipeProvider:
    def __init__(self, recipes:[Recipe]):
        self.recipes = recipes
        # This really needs to be implemented more flexibly
        delivery_cannon = [r.name for r in recipes if "se-delivery-cannon-pack" in r.name]
        recycling = [r.name for r in recipes if "se-recycle" in r.name]
        inferior_simulations = [
            r.name for r in recipes if "se-simulation" in r.name if not "asbm" in r.name
        ]
        inferior_simulations = [
            r.name for r in recipes if not "se-simulation-b" == r.name if 'se-simulation' in r.name
        ]
        blocklist = inferior_simulations + delivery_cannon + ["coal-liquefaction"] + recycling + [
            'se-processing-unit-holmium','se-heat-shielding-iridium','se-low-density-structure-beryllium']
        self.blocklist = blocklist

    def by_name(self, name):
        if name == 'electronic-circuit':
            name = 'electronic-circuit-stone'
        for r in self.recipes:
            if r.name == name:
                return r
        print(f"Could not find recipe for {name}")
        print("Available recipes:")
        for recipe in self.name_includes(name):
            print(recipe.name)
            raise ValueError(f"Recipe {name} not found")

    def name_includes(self, name):
        return [r for r in self.recipes if name in r.name]

    def as_dataframe(self):
        recipes_df = pd.DataFrame(
            [r.to_series() for r in self.recipes]).fillna(0).T
        recipes_df.drop(self.blocklist, axis=1, inplace=True)
        return recipes_df
    def verify(self,target):
        # verify that target can be built from ingredients in the recipe provider
        try:
            target_recipe = self.by_name(target)
        except ValueError:
            print(f"Could not find recipe for {target}")
            print("Available recipes:")
            for recipe in self.name_includes(target):
                print(recipe.name)
            raise ValueError(f"Recipe {target} not found")
        for product in target_recipe.products:
            if product.type == 'free':
                continue
            if product.type == 'item':
                self.verify(product.name)
