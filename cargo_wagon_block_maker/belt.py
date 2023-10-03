from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.prototypes.transport_belt import TransportBelt


def belt(source, destination, name='transport_belt'):
    g = Group()
    if source[0] == destination[0]:
        s,d=(source,destination) if source[1] < destination[1] else (destination,source)
        for y in range(int(s[1]), int(d[1])):
            g.entities.append(TransportBelt(**{
                "name": "transport-belt",
                "position": {
                    "x": source[0],
                    "y": y
                },
                "direction": Direction.SOUTH if source[1] < destination[1] else Direction.NORTH,
            }))
    elif source[1] == destination[1]:
        s,d=(source,destination) if source[0] < destination[0] else (destination,source)
        for x in range(int(s[0]), int(d[0])):
            g.entities.append(TransportBelt(**{
                "name": "transport-belt",
                "position": {
                    "x": x,
                    "y": source[1]
                },
                "direction": Direction.EAST if source[0] < destination[0] else Direction.WEST,
            }))
    else:
        raise ValueError(f'Cannot create belt from {source} to {destination}')
    return g
