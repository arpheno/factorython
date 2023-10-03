import pandas as pd

from data_structures.recipe import Recipe, Product


class RecipeProvider:
    def __init__(self, recipes, ltn_materials):
        self.recipes = recipes
        self.recipes.extend([
            Recipe(
                name=f"ltn {name}",
                ingredients=[],
                products=[Product(name=name, amount=1, type="free")],
                energy=1,
                category="free",
            )
            for name in ltn_materials])
        # This really needs to be implemented more flexibly
        delivery_cannon = [r.name for r in recipes if "se-delivery-cannon-pack" in r.name]
        recycling = [r.name for r in recipes if "se-recycle-radar" in r.name]
        inferior_simulations = [
            r.name for r in recipes if "se-simulation" in r.name if not "asbm" in r.name
        ]
        blocklist = inferior_simulations + delivery_cannon + ["coal-liquefaction"]+recycling+['se-processing-unit-holmium']
        self.blocklist = blocklist

    def by_name(self, name):
        if name=='electronic-circuit':
            name='electronic-circuit-stone'
        for r in self.recipes:
            if r.name == name:
                return r
        raise ValueError(f"Recipe {name} not found")

    def name_includes(self, name):
        return [r for r in self.recipes if name in r.name]

    def as_dataframe(self):
        recipes_df = pd.DataFrame(
            [r.to_series() for r in self.recipes]).fillna(0).T
        recipes_df.drop(self.blocklist, axis=1, inplace=True)
        return recipes_df
