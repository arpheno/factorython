from parsing.prototype_parser import parse_prototypes


def test_parse_prototypes():
    # write a pytest unit test for the above function, you can get data from the file data/entity_prototypes.json
    prototypes_path = "data/entity_prototypes.json"
    with open(prototypes_path, "r") as f:
        prototypes = json.load(f)
    assert parse_prototypes(prototypes) == {'crafting': [
        {'type': 'recipe', 'name': 'se-advanced-circuit', 'energy_required': 6,
         'ingredients': {'se-circuit-board': 2, 'se-copper-cable': 4, 'se-solder': 2}, 'result': 'se-advanced-circuit',
         'result_count': 1, 'category': 'crafting', 'subgroup': 'se-circuit', 'order': 'a[advanced-circuit]'},
        {'type': 'recipe', 'name': 'se-advanced-circuit-2', 'energy_required': 6,
         'ingredients': {'se-circuit-board': 2, 'se-copper-cable': 4, 'se-solder': 2}, 'result': 'se-advanced-circuit',
         'result_count': 1, 'category': 'crafting', 'subgroup': 'se-circuit', 'order': 'a[advanced-circuit]'}],
                                            'crafting-with-fluid': [{'type': 'recipe', 'name': 'se-advanced-circuit-3',
                                                                     'energy_required': 6,
                                                                     'ingredients': {'se-circuit-board': 2,
                                                                                     'se-copper-cable': 4,
                                                                                     'se-solder': 2},
                                                                     'result': 'se-advanced-circuit', 'result_count': 1,
                                                                     'category': 'crafting-with-fluid',
                                                                     'subgroup': 'se-circuit',
                                                                     'order': 'a[advanced-circuit]'}]}
