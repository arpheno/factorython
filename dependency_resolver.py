from typing import List, Dict

from parsed_data import Recipe


def construct_dependency_tree(recipes: List[Recipe], main_product: str) -> Dict[str, List[str]]:
    dependency_tree = {}

    def add_dependencies(product: str):
        recipe = next((r for r in recipes if r.main_product == product), None)
        if recipe:
            if product not in dependency_tree:
                dependency_tree[product] = []
            for ingredient in recipe.ingredients:
                dependency_tree[product].append(ingredient)
                add_dependencies(ingredient)

    add_dependencies(main_product)
    return dependency_tree