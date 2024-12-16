from instance.handling.handling import Handling
from instance.state.game_state import GameState
from instance.state.flags import Flags, set_flag_attr
from instance.state.handling_state import HandlingState
from instance.logic.four import Four

class GameInstance():
    def __init__(self, ID, Config, TimingStruct, HandlingConfig, GameParameters):
        
        self.ID = ID
        self.Config = Config
        self.GameParameters = GameParameters
        
        self.TimingStruct = TimingStruct
        
        self.HandlingConfig = HandlingConfig
        self.HandlingStruct = HandlingState()
        
        self.FlagStruct = Flags()
        self.GameInstanceStruct = GameState()
        
        self.HandlingLogic = Handling(
            self.Config, 
            self.HandlingConfig, 
            self.HandlingStruct, 
            self.FlagStruct, 
        )
        
        self.GameLogic = Four(
            self.Config,
            self.FlagStruct, 
            self.GameInstanceStruct, 
            self.TimingStruct, 
            self.HandlingStruct, 
            self.HandlingConfig, 
            matrix_width = self.GameParameters['MATRIX_WIDTH'], 
            matrix_height = self.GameParameters['MATRIX_HEIGHT'],
            rotation_system = self.GameParameters['ROTATION_ SYSTEM'],
            randomiser = self.GameParameters['RANDOMISER'], 
            queue_previews = self.GameParameters['QUEUE_PREVIEWS'], 
            seed = self.GameParameters['SEED'], 
            hold = self.GameParameters['HOLD_ENABLED'], 
            allowed_spins = self.GameParameters['ALLOWED_SPINS'], 
            lock_out_ok = self.GameParameters['LOCK_OUT_OK'],
            top_out_ok = self.GameParameters['TOP_OUT_OK'],
            reset_on_top_out = self.GameParameters['RESET_ON_TOP_OUT']
        )
             
    def do_game_tick(self):
        self.GameLogic.tick()
    
    def do_handling_tick(self):
        self.HandlingLogic.tick()