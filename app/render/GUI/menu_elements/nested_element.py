class NestedElement():
    def __init__(self, parent = None):
        """
        A helper class for elements that are nested in other elements
        """
        self.parent = parent

    def get_local_position(self):
        """
        Get the position of the element relative to the container it is in for collision detection
        """
        return 0, 0

    def get_screen_position(self):
        """
        Get the position of the element on the screen for collision detection
        """
        local_x, local_y = self.get_local_position()

        if self.parent:
            parent_x, parent_y = self.parent.get_screen_position()
            return local_x + parent_x, local_y + parent_y

        return local_x, local_y