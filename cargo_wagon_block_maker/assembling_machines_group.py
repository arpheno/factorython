from draftsman.classes.group import Group


class AssemblingMachinesGroup(Group):
    def __init__(self, flows, **kwargs):
        super().__init__(**kwargs)
        self.flows = flows

    @property
    def groups(self):
        def chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i: i + n]

        # order entities first by x then by y with sorted
        ordered_entities = sorted(self.entities, key=lambda x: (x.global_position['x'], x.global_position['y']))

        production_sites_around_wagon = list(chunks(ordered_entities, 4))
        production_sites_around_wagon = [ChunkProxy(chunk) for chunk in production_sites_around_wagon]
        return production_sites_around_wagon

    @property
    def top_row(self):
        # order first by y then by x
        ordered_entities = sorted(self.entities, key=lambda x: (x.global_position['y'], x.global_position['x']))
        return ordered_entities[: len(self.entities) // 2]

    @property
    def bottom_row(self):
        return self.entities[len(self.entities) // 2:]


class ChunkProxy:
    def __init__(self, chunk):
        self.chunk = chunk

    def __getitem__(self, item):
        return self.chunk[item]

    @property
    def items_used(self):
        return set(sum((list(machine.import_export.keys()) for machine in self.chunk), []))
