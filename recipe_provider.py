import pandas as pd
from rapidfuzz import process, fuzz

from data_structures.recipe import Recipe, Product


class RecipeProvider:
    def __init__(self, recipes: [Recipe], top_n_similar_recipes_to_show=5):
        self.recipes = recipes
        self.top_n_similar_recipes_to_show = top_n_similar_recipes_to_show
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
            'se-processing-unit-holmium', 'se-heat-shielding-iridium', 'se-low-density-structure-beryllium']
        self.blocklist = blocklist

    def by_name(self, name):
        if name == 'electronic-circuit':
            name = 'electronic-circuit-stone'
        for r in self.recipes:
            if r.name == name:
                return r
        raise ValueError(f'Could not find recipe for {name}')

    def iterator_over_possible_candidates(self, name):
        sorted_recipe_names = self.find_recipe(name)
        for recipe_name in sorted_recipe_names[:self.top_n_similar_recipes_to_show]:
            yield recipe_name

    def name_included_in(self, name):
        return [r for r in self.recipes if name + "-" in r.name]

    def name_includes(self, name):
        return [r for r in self.recipes if r.name in name]

    def find_recipe(self, name):
        # Calculate similarity scores for all recipes
        recipe_names = [recipe.name for recipe in self.recipes]
        results = process.extract(name, recipe_names, scorer=fuzz.ratio, limit=len(recipe_names))

        # Sort recipes by similarity score in descending order
        sorted_recipes = sorted(results, key=lambda x: x[1], reverse=True)

        # Extract sorted recipes
        sorted_recipe_names = [recipe[0] for recipe in sorted_recipes]
        return sorted_recipe_names

    def name_includes_word_of_candidate(self, name):
        results = []
        for r in self.recipes:
            for word in r.name.split('-'):
                if word in name.split('-') and word != 'se':
                    print(f"Appending {r.name} because {word} is in {name}")
                    results.append(r)
        return results

    def as_dataframe(self):
        recipes_df = pd.DataFrame(
            [r.to_series() for r in self.recipes]).fillna(0).T
        recipes_df.drop(self.blocklist, axis=1, inplace=True)
        return recipes_df

    def verify(self, target):
        # verify that target can be built from ingredients in the recipe provider
        try:
            target_recipe = self.by_name(target)
        except ValueError:
            print(f"Could not find recipe for {target}")
            print("Available recipes:")
            for recipe in self.name_includes_word_of_candidate(target):
                print(recipe.name)
            raise ValueError(f"Recipe {target} not found")
        for product in target_recipe.products:
            if product.type == 'free':
                continue
            if product.type == 'item':
                self.verify(product.name)
