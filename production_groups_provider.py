from recipe_provider import RecipeProvider


class ProductionGroupsProvider:
    def __init__(self, recipe_provider: RecipeProvider):
        self.recipe_provider = recipe_provider

    def science_packs_4(self):
        four_packs = self.recipe_provider.name_includes("science-pack-4")
        other_packs = [
            self.recipe_provider.by_name(r)
            for r in [
                "se-rocket-science-pack",
                "utility-science-pack",
                "production-science-pack",
            ]
        ]
        return four_packs + other_packs
    def science_packs_4_deepless(self):
        return [r for r in self.science_packs_4() if not "deep" in r.name]

    def catalogues(self):
        return self.recipe_provider.name_includes("catalogue")
equipment = [
    'jetpack-2',
    'battery-equipment',
    'belt-immunity-equipment',
    'exoskeleton-equipment',
    'se-rtg-equipment',
    'night-vision-equipment',
    'power-armor-mk2',
    # 'se-lifesupport-equipment-1',
    'personal-roboport-mk2-equipment',
    # 'se-thruster-suit',
    'personal-laser-defense-equipment',
    'arithmetic-combinator',
    'constant-combinator',
    'decider-combinator',
    'ltn-combinator',
    'iron-chest',
    'steel-chest',
    'logistic-chest-active-provider',
    'logistic-chest-passive-provider',
    'logistic-chest-storage',
    'logistic-chest-buffer',
    'logistic-chest-requester',
    'se-delivery-cannon-chest',
    'pump',
    'pumpjack',
    'construction-robot',
    'logistic-robot',


]
second=['se-condenser-turbine',
        'small-lamp','productivity-module-3',
        'cargo-wagon',
        'logistic-train-stop',
        'oil-refinery',
        'rail-signal',
        'rail-chain-signal',
        'long-handed-inserter',
        ]
