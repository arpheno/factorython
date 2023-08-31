from dataclasses import dataclass
from typing import List

from draftsman.classes.entity import Entity


@dataclass
class Cell:
    input_loaders: List[Entity]
    middle_loaders: List[Entity]
    output_loaders: List[Entity]
    input_pumps: List[Entity]
    output_pumps: List[Entity]
    combinators: List[Entity]
    assembly_machine: Entity
