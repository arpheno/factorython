import json

from building_resolver import BuildingResolver
from data_structures.recipe import Recipe, Ingredient, Product
from production_groups_provider import ProductionGroupsProvider
from production_line_builder import ProductionLineBuilder
from parsing.prototype_parser import parse_prototypes
from parsing.recipe_parser import parse_recipes
from recipe_provider import RecipeProvider

basic_materials = [
    "water",
    "crude-oil",
    "coal",
    "iron-ore",
    "copper-ore",
    "stone",
    "uranium-ore"
]
nauvis_materials = [
    "copper-plate",
    "copper-cable",
    "low-density-structure",
    "heat-shielding",
    "iron-plate",
    "steel-plate",
    "stone-tablet",
    "stone-brick",
    "petroleum-gas",
    "heavy-oil",
    "light-oil",
    "glass",
    "sulfur",
    "advanced-circuit",
    "plastic-bar",
    "firearm-magazine",
    "locomotive",
    "lubricant",
    "uranium-235",
    "uranium-238",
    "explosives",
    "concrete",
    "storage-tank",
    "sulfuric-acid",
    "sand",
    "electronic-circuit",
    "battery",
    "electric-furnace",
    "accumulator",
    "solid-fuel",
    "heat-shielding",
    'uranium-fuel-cell',
    'solar-panel',
    'speed-module',
    'electronic-circuit',
    'satellite',
    'effectivity-module',
    'rocket-control-unit',
    'rocket-fuel',
    'productivity-module'
]
se_materials = [
    'se-iron-ingot',
    'se-copper-ingot',
    "se-material-testing-pack",
    "se-holmium-cable",
    "se-holmium-ingot",
    "se-holmium-plate",
    "se-holmium-solenoid",
    "se-vulcanite-block",
    "se-iridium-ingot",
    "se-iridium-plate",
    "se-heavy-girder",
    "se-heavy-bearing",
    "se-beryllium-ingot",
    "se-beryllium-plate",
    "se-aeroframe-pole",
    "se-aeroframe-scaffold",
    "se-cryonite-rod",
    "se-cryonite-slush",
    "se-core-fragment-se-vitamelange",
    "se-data-storage-substrate",
    "se-vitalic-reagent",
    "se-vitalic-epoxy",
    "se-vitalic-acid",
    "se-vulcanite-block",
    "se-vitamelange-bloom",
    "se-vitamelange-spice",
    "se-vitamelange-extract",
    "se-methane-gas",
    "se-heavy-composite",
]

if __name__ == "__main__":
    recipes_path = "data/recipes.json"
    assembly_path = "data/assembly_machine.json"
    with open(assembly_path, "r") as f:
        assembly = json.load(f)
    with open(recipes_path, "r") as f:
        recipes = json.load(f)
    crafting_categories = parse_prototypes(assembly)
    recipes = parse_recipes(recipes)
    probe_recipes = [
        Recipe(
            name="se-star-data",
            products=[Product(name="se-star-probe-data", amount=1000, type="item")],
            ingredients=[Ingredient(name="se-star-probe", amount=1, type="item")],
            energy=1000,
            category="se-space-probe-launch",
        ),
        Recipe(
            name="se-belt-probe-data",
            products=[Product(name="se-belt-probe-data", amount=1000, type="item")],
            ingredients=[Ingredient(name="se-belt-probe", amount=1, type="item")],
            energy=1000,
            category="se-space-probe-launch",
        ),
        Recipe(
            name="se-satellite-telemetry",
            products=[Product(name="se-satellite-telemetry", amount=100, type="item")],
            ingredients=[Ingredient(name="satellite", amount=1, type="item")],
            energy=1000,
            category="se-space-probe-launch",
        ),
    ]
    recipes.extend(probe_recipes)
    nauvis_materials.extend(se_materials)
    building_resolver = BuildingResolver(crafting_categories)
    delivery_cannon = [r.name for r in recipes if "se-delivery-cannon-pack" in r.name]
    inferior_simulations = [
        r.name for r in recipes if "se-simulation" in r.name if not "asbm" in r.name
    ]
    blacklist = inferior_simulations + delivery_cannon + ["coal-liquefaction"]
    recipe_provider = RecipeProvider(
        recipes, basic_materials, nauvis_materials, blacklist
    )

    production_group_provider = ProductionGroupsProvider(recipe_provider)
    packs = production_group_provider.science_packs_4_deepless()
    product_quantities = [(r.name, 1) for r in packs]

    production_line_builder = ProductionLineBuilder(recipe_provider, building_resolver)
    # line = production_line_builder.build([("se-chemical-gel", 1.0)])
    line = production_line_builder.build([("se-biological-science-pack-4", 1.0)])
    # line = production_line_builder.build(product_quantities)
    line.print()
    connections = production_line_builder.organize(line)
    print(connections)