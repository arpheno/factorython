class FakeAssemblyMachine:
    def __init__(self, name, crafting_speed=1):
        self.name = name
        self.crafting_speed = crafting_speed
        self.module_specification = None
