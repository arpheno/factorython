import math
from collections import defaultdict
from itertools import product, cycle

from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.error import InvalidRecipeError
from draftsman.prototypes.assembling_machine import AssemblingMachine

from materials import trash
from recipe_provider import RecipeProvider
from space.liquids import barreler


def select_fluid_boxes(boxes, fluids):
    ratio = len(boxes) // len(fluids) if fluids else 1
    # yield chunks of boxes in chunksize ratio
    box_mapping = sorted([fluid for box, fluid in zip(boxes, cycle(fluids))], key=fluids.index)
    fluid_box_by_resource = defaultdict(list)
    for fluid, box in zip(box_mapping, boxes):
        fluid_box_by_resource[fluid].append(box)
    result_boxes = []
    for p in product(*fluid_box_by_resource.values()):
        # print(p)
        for box1, box2 in product([b.position for b in p], [b.position for b in p]):
            # print(box1,box2)
            if 0 < abs(box1[0] - box2[0]) < 3 or 0 < abs(box1[1] - box2[1]) < 3:
                # print('too close')
                break
        else:
            # print(f'candidate found:{p}')
            break

    return {fluid: box for fluid, box in zip(fluids, p)}


def robot_connected_space_machine(
        building_resolver, recipe_provider: RecipeProvider, recipe: str
):
    g = Group()
    R = recipe_provider.by_name(recipe)
    prototype = building_resolver(R)
    ingredient_fluids = [f for f in R.ingredients if f.type == "fluid"]
    product_fluids = [f for f in R.products if f.type == "fluid"]
    input_fluid_boxes = [
        f.pipe_connections[0]
        for f in prototype.fluid_boxes
        if f.pipe_connections[0].type == "input"
    ]
    output_fluid_boxes = [
        f.pipe_connections[0]
        for f in prototype.fluid_boxes
        if f.pipe_connections[0].type == "output"
    ]
    input_box_ratio = (
        len(input_fluid_boxes) // len(ingredient_fluids) if ingredient_fluids else 1
    )
    output_box_ratio = (
        len(output_fluid_boxes) // len(product_fluids) if product_fluids else 1
    )
    top = min([b.position[1] for b in input_fluid_boxes + output_fluid_boxes])
    bottom = max([b.position[1] for b in output_fluid_boxes + input_fluid_boxes])
    left = min([b.position[0] for b in input_fluid_boxes + output_fluid_boxes])
    right = max([b.position[0] for b in output_fluid_boxes + input_fluid_boxes])
    input_box_mapping = select_fluid_boxes(input_fluid_boxes, ingredient_fluids)
    for fluid, box in input_box_mapping.items():
        b = barreler("empty", fluid.name, fluid.amount*10)
        if not b.entities:
            continue
        if box.position[1] == top:
            b.rotate(4)
            b.translate(0, -(b.entities["machine"].tile_height // 2))
        elif box.position[1] == bottom:
            b.rotate(0)
            b.translate(0, +b.entities["machine"].tile_height // 2)
        elif box.position[0] == left:
            b.rotate(2)
            b.translate(-(b.entities["machine"].tile_width // 2), 0)
        elif box.position[0] == right:
            b.rotate(6)
            b.translate(+(b.entities["machine"].tile_width // 2), 0)
        b.translate(*box.position)
        g.entities.append(b)
    for fluid, box in zip(product_fluids, output_fluid_boxes[::output_box_ratio]):
        b = barreler("fill", fluid.name, fluid.average_amount*10,provider_chest_name='logistic-chest-active-provider' if fluid.name in trash else 'logistic-chest-passive-provider')
        if not b.entities:
            # The liquid couldn't be barreled,
            continue
        if box.position[1] == top:
            b.rotate(4)
            b.translate(0, -(b.entities["machine"].tile_height // 2))
        elif box.position[1] == bottom:
            b.rotate(0)
            b.translate(0, +b.entities["machine"].tile_height // 2)
        elif box.position[0] == left:
            b.rotate(2)
            b.translate(-(b.entities["machine"].tile_width // 2), 0)
        elif box.position[0] == right:
            b.rotate(6)
            b.translate(+(b.entities["machine"].tile_width // 2), 0)
        b.translate(*box.position)
        g.entities.append(b)
    machine = AssemblingMachine(
        name=prototype.name,
        recipe=R.name,
        id="machine",
        position={"x": 0, "y": 0},
    )
    g.entities.append(machine)
    solid_non_trash_products=[product  for product in R.products if product.name not in trash if product.type== "item" if not product.name in [ingredient.name for ingredient in R.ingredients]]
    solid_infrastructure = [
        {
            "name": "filter-inserter",
            "id": "trash_inserter",
            "position": {"x": left, "y": bottom - 1},
            "direction": Direction.EAST,
            "filters": [product.name for product in solid_non_trash_products],
            "filter_mode": "blacklist",
        },
        # Make an active provider chest for the trash inserter to insert into
        {
            "name": "logistic-chest-active-provider",
            "id": "trash_chest",
            "position": {"x": left - 1, "y": bottom - 1},
        },
        # put a medium electric pole on each corner of the machine
        {"name": "medium-electric-pole", 'id':'bla',"position": {"x": left, "y": top}},
        {"name": "medium-electric-pole", "position": {"x": right, "y": top}},
        {"name": "medium-electric-pole", "position": {"x": left, "y": bottom}},
        {"name": "medium-electric-pole", "position": {"x": right, "y": bottom}},
    ]
    if [t for t in R.ingredients if t.type == "item"]:
        solid_infrastructure.extend(
            [
                {
                    "name": "fast-inserter",
                    "id": "input_inserter",
                    "position": {"x": right - 1, "y": bottom},
                    "direction": Direction.SOUTH,
                },
                # Make a requester chest for the input inserter to take from
                {
                    "name": "logistic-chest-requester",
                    "id": "input_chest",
                    "position": {"x": right - 1, "y": bottom + 1},
                    "request_filters": [
                        {"name": ingredient.name, "count": math.ceil(ingredient.amount * 10), "index": i + 1}
                        for i, ingredient in enumerate(R.ingredients)
                        if ingredient.type == "item"
                    ],
                },
            ]
        )
        if any(solid_non_trash_products):
            solid_infrastructure.extend(
                [
                    {
                        "name": "filter-inserter",
                        "id": "output_inserter",
                        "position": {"x": left + 1, "y": bottom} if not g.find_entity_at_position((left + 1,bottom)) else {'x':right-2,'y':bottom},
                        "direction": Direction.NORTH,
                        "filters": [product.name for product in solid_non_trash_products],
                        "filter_mode": "whitelist",
                    },
                    # Make an passive provider chest for the output inserter to insert into
                    {
                        "name": "logistic-chest-passive-provider",
                        "id": "output_chest",
                        "position": {"x": left + 1, "y": bottom+1} if not g.find_entity_at_position((left + 1,bottom)) else {'x':right-2,'y':bottom+1},
                        "bar": 1,
                    },
                ]
            )
    solid_infrastructure_group = Group(entities=solid_infrastructure)
    g.entities.append(solid_infrastructure_group)
        # g.generate_power_connections()
    return g
