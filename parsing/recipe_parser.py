from data_structures.recipe import Recipe


def parse_recipes(recipes:dict):
    recipes = list(recipes.values())
    for r in recipes:
        #sometimes the ingredients or products can be empty dictionaries, in that case change them to empty lists
        if r['ingredients'] == {}:
            r['ingredients'] = []
        if r['products'] == {}:
            r['products'] = []
    parsed_recipes = [Recipe(**r) for r in recipes]
    parsed_recipes = [r for r in parsed_recipes if not r.name.startswith('ee-')]
    return parsed_recipes
