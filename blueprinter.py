from draftsman.blueprintable import Blueprint, BlueprintBook
from draftsman.classes.group import Group
from copy import deepcopy


class MachineCell:
    def __init__(self, machine_cell: Group):
        self.train_stops = (
            machine_cell.find_entities_filtered(name="logistic-train-stop")[0],
            machine_cell.find_entities_filtered(name="logistic-train-stop")[-1],
        )
        machine_cell.translate(
            -self.train_stops[0].position["x"], -self.train_stops[0].position["y"]
        )
        self.cell = machine_cell
        self.characteristic_distance = self.train_stop_distance(
            self.train_stops[0], self.train_stops[1]
        )

    def translate(self, x, y):
        self.cell.translate(x, y)

    def align(self, other) -> [(int, int)]:
        possible_grid_positions = []
        for stop1 in other.find_entities_filtered(name="logistic-train-stop"):
            for stop2 in other.find_entities_filtered(name="logistic-train-stop"):
                if (
                    self.train_stop_distance(stop1, stop2)
                    == self.characteristic_distance
                ):
                    possible_grid_positions.append(stop1.position)
        return possible_grid_positions

    def train_stop_distance(self, stop1, stop2):
        return stop1.position - stop2.position


with open("data/cells.factorio") as f:
    cells = BlueprintBook(f.read())
with open("data/45skeleton.factorio") as f:
    block = Blueprint(f.read())
nine_by_twelve_cell = Group()
nine_by_twelve_cell.load_from_string(blueprint_string=cells.blueprints[0].to_string())
nine_by_twelve_cell = MachineCell(nine_by_twelve_cell)
possible_grid_positions = nine_by_twelve_cell.align(block)

for grid_position in possible_grid_positions[0::2]:
    cell = deepcopy(nine_by_twelve_cell)
    cell.translate(grid_position["x"], grid_position["y"])
    block.entities.append(cell.cell)

print(block.to_string())
