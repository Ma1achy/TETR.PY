class NestedElement():
    def __init__(self, parent = None):
        self.parent = parent

    def get_local_position(self):
        return 0, 0

    def get_screen_position(self):
        local_x, local_y = self.get_local_position()

        if self.parent:
            parent_x, parent_y = self.parent.get_screen_position()
            return local_x + parent_x, local_y + parent_y

        return local_x, local_y