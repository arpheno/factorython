from typing import List

from recipe import Recipe


def find_recipes_that_make_product(product_name:str, recipes:List[Recipe]) -> List[Recipe]:
    recipes_that_produce_product = []
    for r in recipes:
        if 'barrel' in r.name:
            continue
        for p in r.products:
            if p.name == product_name:
                recipes_that_produce_product.append(r)
    return recipes_that_produce_product
