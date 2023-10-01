import dataclasses


@dataclasses.dataclass
class Module:
    name: str
    speed: float
    consumption: float
    pollution: float
    def __add__(self, other):
        return Module(
            name=self.name,
            speed=self.speed + other.speed,
            consumption=self.consumption + other.consumption,
            pollution=self.pollution + other.pollution,
        )
    def __mul__(self, other):
        return Module(
            name=self.name,
            speed=self.speed * other,
            consumption=self.consumption * other,
            pollution=self.pollution * other,
        )


class ModuleBuilder:
    def __init__(self, modules):
        self.modules = modules
    def build(self, module_name):
        module = self.modules[module_name]
        return Module(
            name=module_name,
            speed=module['effect']['speed']['bonus'],
            consumption=module['effect']['consumption']['bonus'],
            pollution=module['effect']['pollution']['bonus'],
        )
