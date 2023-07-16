from recipe import Recipe, Product
from recipe_parser import parse_recipes


def test_recipe_parsing():
    recipe_data = {
        "name": "se-experimental-specimen",
        "category": "space-growth",
        "products": [
            {
                "type": "item",
                "name": "se-experimental-specimen",
                "probability": 1,
                "amount_min": 5,
                "amount_max": 10
            },
            {
                "type": "item",
                "name": "se-specimen",
                "probability": 1,
                "amount_min": 0,
                "amount_max": 5
            },
            {
                "type": "fluid",
                "name": "se-contaminated-bio-sludge",
                "probability": 1,
                "amount": 30
            },
            {
                "type": "fluid",
                "name": "se-contaminated-space-water",
                "probability": 1,
                "amount": 20
            }
        ],
        "ingredients": [
            {
                "type": "item",
                "amount": 10,
                "name": "se-experimental-bioculture"
            },
            {
                "type": "fluid",
                "amount": 100,
                "name": "se-nutrient-gel"
            }
        ],
        "hidden": False,
        "energy": 80,
        "order": "z-05"
    }

    recipe = Recipe(**recipe_data)

    assert recipe.name == "se-experimental-specimen"
    assert recipe.category == "space-growth"
    assert len(recipe.products) == 4
    assert recipe.products[0].name == "se-experimental-specimen"
    assert recipe.ingredients[0].name == "se-experimental-bioculture"
    assert recipe.hidden == False
    assert recipe.energy == 80
    assert recipe.order == "z-05"
def test_product_with_min_max_and_probability():
    product = Product(
        type="item",
        name="se-experimental-specimen",
        amount_min=5,
        amount_max=10,
        probability=1
    )
    assert product.average_amount == 7.5

def test_product_with_amount():
    product = Product(
        type="item",
        name="se-experimental-specimen",
        amount=8
    )
    assert product.average_amount == 8

def test_product_without_enough_information():
    product = Product(
        type="item",
        name="se-experimental-specimen",
        amount_min=5,
        probability=1
    )
    assert product.average_amount is None

def test_parse_recipes():
    recipes = {
        "se-core-miner": {
            "name": "se-core-miner",
            "category": "crafting",
            "products": [
                {
                    "type": "item",
                    "name": "se-core-miner",
                    "probability": 1,
                    "amount": 1
                }
            ],
            "ingredients": [
                {
                    "type": "item",
                    "amount": 200,
                    "name": "electronic-circuit"
                },
                {
                    "type": "item",
                    "amount": 400,
                    "name": "concrete"
                },
                {
                    "type": "item",
                    "amount": 40,
                    "name": "electric-mining-drill"
                },
                {
                    "type": "item",
                    "amount": 100,
                    "name": "steel-plate"
                }
            ],
            "hidden": False,
            "energy": 100,
            "order": "zzz-core-miner"
        },
        "se-experimental-specimen": {
            "name": "se-experimental-specimen",
            "category": "space-growth",
            "products": [
                {
                    "type": "item",
                    "name": "se-experimental-specimen",
                    "probability": 1,
                    "amount_min": 5,
                    "amount_max": 10
                },
                {
                    "type": "item",
                    "name": "se-specimen",
                    "probability": 1,
                    "amount_min": 0,
                    "amount_max": 5
                },
                {
                    "type": "fluid",
                    "name": "se-contaminated-bio-sludge",
                    "probability": 1,
                    "amount": 30
                },
                {
                    "type": "fluid",
                    "name": "se-contaminated-space-water",
                    "probability": 1,
                    "amount": 20
                }
            ],
            "ingredients": [
                {
                    "type": "item",
                    "amount": 10,
                    "name": "se-experimental-bioculture"
                },
                {
                    "type": "fluid",
                    "amount": 100,
                    "name": "se-nutrient-gel"
                }
            ],
            "hidden": False,
            "energy": 80,
            "order": "z-05"
        }
    }

    parsed_recipes = parse_recipes(recipes)
    assert len(parsed_recipes) == 2
    assert parsed_recipes[0].name == "se-core-miner"
    assert parsed_recipes[1].name == "se-experimental-specimen"

# Run the test
