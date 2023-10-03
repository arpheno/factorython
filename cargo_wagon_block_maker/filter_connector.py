from draftsman.classes.group import Group


def filter_connector(mat1, mat2):
    g = Group(entities=[{'name': 'stack-filter-inserter',
                         'position': {'x': x, 'y': y},
                         'direction': 6} for x in range(2) for y in range(2)])
    g.entities[0].control_behavior = {'circuit_mode_of_operation': 3,
                                      'circuit_read_hand_contents': True,
                                      'circuit_hand_read_mode': 1}
    g.entities[0].filters = [{'index': 1, 'name': mat1}]
    g.entities[1].control_behavior = {'circuit_mode_of_operation': 1}
    g.entities[2].control_behavior = {'circuit_mode_of_operation': 3,
                                      'circuit_read_hand_contents': True,
                                      'circuit_hand_read_mode': 1}
    g.entities[2].filters = [{'index': 1, 'name': mat2}]
    g.entities[3].control_behavior = {'circuit_mode_of_operation': 1}
    for entity in g.entities:
        entity.filter_mode = 'blacklist'
    g.add_circuit_connection('green', g.entities[0], g.entities[1])
    g.add_circuit_connection('green', g.entities[2], g.entities[3])
    return g


def filter_connector_4(mat1, mat2, mat3='fish', mat4='fish'):
    g = Group(entities=[{'name': 'stack-filter-inserter',
                         'position': {'x': x, 'y': y},
                         'direction': 6} for x in range(2) for y in range(2)])
    g.entities[0].filters = [{'index': 1, 'name': mat1}]
    g.entities[1].filters = [{'index': 1, 'name': mat2}]
    g.entities[2].filters = [{'index': 1, 'name': mat3}]
    g.entities[3].filters = [{'index': 1, 'name': mat4}]
    return g
