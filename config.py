class Config():
    def __init__(self):
        """
        Configuration of the game
        """
        
        self.HANDLING_SETTINGS = {
            'ARR' :33,           # Auto repeat rate (int) in ms: The speed at which tetrominoes move when holding down the movement keys (ms)
            'DAS' :167,          # Delayed Auto Shift (int) in ms: The time between the inital key press and the automatic repeat movement (ms)
            'DCD' :0,            # DAS Cut Delay (int) in ms: If none-zero, any ongoing DAS movement will pause for a set amount of time after dropping/rorating a piece (ms)
            'SDF' : 23,          # Soft Drop Facor (int): The factor the soft dropping scales the current gravity by, or 'inf' for instant soft drop
            'PrevAccHD': True,   # Prevent Accidental Hard Drops (bool): When a piece locks on its own, the harddrop action is disabled for a few frames
            'DASCancel': False,  # Cancel DAS When Changing Directions (bool): If true, the DAS timer will reset if the opposite direction is pressed
            'PrefSD':    True,   # Prefer Soft Drop Over Movement (bool): At very high speeds, the soft drop action will be prioritized over movement
            'PrioriDir': True    # Prioritise the Most Recent Direction (bool): when True if both the left and right keys are held the more recent key to be held will be prioritised, if False no movement will be performed
        }
        
        self.CAPTION = 'Four'
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 1500, 900
        self.FOUR_INSTANCE_WIDTH, self.FOUR_INSTANCE_HEIGHT = 800, 900
        self.BORDER_WIDTH = 5
        
        self.UNCAPPED_FPS = False
        self.FPS = 144
        self.TPS = 256 # Subframes per second
        self.POLLING_RATE = 1000
        
        self.SEED = 0
        self.MATRIX_WIDTH, self.MATRIX_HEIGHT = 10, 40
        self.QUEUE_LENGTH = 5
    
        self.COLOUR_MAP = {
            -1: (255, 0, 0),
            0: (0, 0, 0), # empty
            1: (168, 34, 139), # T
            2: (99, 177, 0), # S
            3: (206, 0, 43), # Z
            4: (219, 87, 0), # L
            5: (38, 64, 202), # J 
            6: (221, 158, 0), # O
            7: (51, 156, 218), # I
            8: (105, 105, 105), # garbage
        }
        
        # Rendering constants
        self.GRID_SIZE = self.FOUR_INSTANCE_WIDTH // 25
        self.MATRIX_WIDTH = self.MATRIX_WIDTH
        self.MATRIX_HEIGHT = self.MATRIX_HEIGHT
        self.MATRIX_SURFACE_WIDTH = self.MATRIX_WIDTH * self.GRID_SIZE
        self.MATRIX_SURFACE_HEIGHT = self.MATRIX_HEIGHT // 2 * self.GRID_SIZE
        self.MATRIX_SCREEN_CENTER_X = (self.FOUR_INSTANCE_WIDTH - self.MATRIX_SURFACE_WIDTH) // 2
        self.MATRIX_SCREEN_CENTER_Y = (self.FOUR_INSTANCE_HEIGHT - self.MATRIX_SURFACE_HEIGHT) // 2