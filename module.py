import dataclasses

from draftsman.data import modules


@dataclasses.dataclass
class Module:
    name: str
    speed: float
    consumption: float
    pollution: float
    productivity: float

    def __add__(self, other):
        return Module(
            name=self.name,
            speed=self.speed + other.speed,
            consumption=self.consumption + other.consumption,
            pollution=self.pollution + other.pollution,
            productivity=self.productivity + other.productivity,
        )

    def __mul__(self, other):
        return Module(
            name=self.name,
            speed=self.speed * other,
            consumption=self.consumption * other,
            pollution=self.pollution * other,
            productivity=self.productivity * other,
        )


class ModuleBuilder:
    def __init__(self, modules):
        self.modules = modules

    def build(self, module_name):
        module = self.modules[module_name]
        return Module(
            name=module_name,
            productivity=module['effect'].get('productivity',{'bonus':0})['bonus'],
            pollution=module['effect'].get('pollution',{'bonus':0})['bonus'],
            consumption=module['effect'].get('consumption',{'bonus':0})['bonus'],
            speed=module['effect'].get('speed',{'bonus':0})['bonus'],

        )
if __name__ == "__main__":
    module=ModuleBuilder(modules.raw).build("productivity-module-2")
    print(module)