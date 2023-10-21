import dataclasses

from draftsman.data.modules import raw as modules


@dataclasses.dataclass
class Module:
    name: str
    speed: float=0
    consumption: float=0
    pollution: float=0
    productivity: float=0

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
    def __call__(self,recipe):
        recipe.products = [
            product * (1 + self.productivity) for product in recipe.products
        ]
        recipe.energy = recipe.energy / (1 + self.speed)
        return recipe


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