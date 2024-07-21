import hmni


class RecipeFinder:
    def __init__(self, recipes):
        self.recipes = recipes
        self.matcher = hmni.Matcher()

    def find_recipe(self, name):
        # Calculate similarity scores for all recipes
        similarities = []
        for recipe in self.recipes:
            score = self.matcher.similarity(name, recipe.name)
            similarities.append((recipe, score))

        # Sort recipes by similarity score in descending order
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Extract sorted recipes
        results = [recipe for recipe, score in similarities]

        for recipe in results:
            print(recipe.name)


# Example usage
class Recipe:
    def __init__(self, name):
        self.name = name


recipes = [Recipe("Spaghetti Bolognese"), Recipe("Chicken Alfredo"), Recipe("Beef Stroganoff")]

finder = RecipeFinder(recipes)
finder.find_recipe("Spagetti Bolognes")
