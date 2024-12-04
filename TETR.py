import threading
from config import StructConfig
from instance.handling.handling import Handling
import time
from instance.handling.handling_config import HandlingConfig
from core.state.struct_debug import StructDebug
from core.state.struct_gameinstance import StructGameInstance
from core.state.struct_flags import StructFlags, set_flag_attr
from core.state.struct_handling import StructHandling
from render.render_new import StructRender
from instance.four import Four
from core.clock import Clock
import pygame
import queue
import os
from render.render_new import Render
from app.input_manager import InputManager
from app.game_instance_manager import GameInstanceManager
from app.menu_kb_input_handler import MenuKeyboardInputHandler, UIAction
from app.debug_manager import DebugManager
from app.pygame_event_handler import PygameEventHandler
from app.state.timing import Timing
from app.menu_manager import MenuManager
from app.mouse_input_handler import MouseInputHandler
from app.state.keyboard import Keyboard
from app.state.mouse import Mouse

#TODO: change renderer methods to NOT use methods ASSOCIATED WITH A GAME INSTANCE
#      change game instance to UPDATE variables, i.e, current_tetromino is on floor etc which are contained in GameInstanceStruct
#      GameInstanceStruct will have to be contained in a Queue or something so that the renderer can access it in a thread safe way
#      Debug Menu will have to be changed in a similar way but ALSO, there will have to be per game instance debug info

#TODO: implement mouse event handling in the menus, probably best way to do it is the currently active menu passes the events and mouse positions to all the buttons
# then the buttons just look at the events, i.e mouse click and test if the mouse position is within the button if it is consume the action and then do it.

class App():
    def __init__(self):
        
        self.is_focused = False
        self.PRINT_WARNINGS = True
        self.game_instances = []
        
        self.Keyboard = Keyboard()
        self.Mouse = Mouse()
        
        self.Config = StructConfig()    
        self.Timing = Timing()
        self.FrameClock = Clock()
        
        self.RenderStruct = StructRender()
        self.DebugStruct = StructDebug()
        self.HandlingConfig = HandlingConfig()
        
        self.MouseInputHandler = MouseInputHandler(self.Mouse)
        
        self.__init_pygame()
        self.__register_event_handlers()
        
        self.menu_key_bindings = {
            UIAction.MENU_LEFT:         ['left'],
            UIAction.MENU_RIGHT:        ['right'],
            UIAction.MENU_UP:           ['up'],
            UIAction.MENU_DOWN:         ['down'],
            UIAction.MENU_CONFIRM:      ['enter'],
            UIAction.MENU_BACK:         ['esc'],
            UIAction.MENU_DEBUG:        ['f3'],
            UIAction.WINDOW_FULLSCREEN: ['f11'],
        }
   
        self.InputManager = InputManager(self.Keyboard, self.Timing, self.PRINT_WARNINGS)
        self.MenuInputHandler = MenuKeyboardInputHandler(self.Keyboard, self.menu_key_bindings, self.Timing, self.PRINT_WARNINGS)
        self.MenuManager = MenuManager(self.Keyboard, self.Mouse, self.Config, self.Timing, self.RenderStruct, self.DebugStruct)
        self.GameInstanceManager = GameInstanceManager(self.Timing, self.PRINT_WARNINGS)
        self.Render = Render(self.Config, self.Timing, self.RenderStruct, self.DebugStruct, self.game_instances, self.MenuManager)
        self.Debug = DebugManager(self.Config, self.Timing, self.RenderStruct, self.DebugStruct)
        
        self.GameParameters = { # temp, will be pased to game instance upon creation. This dict will be created by the menu manager
            'MATRIX_WIDTH': 10,
            'MATRIX_HEIGHT': 20,
            'ROTATION_SYSTEM': 'SRS',
            'RANDOMISER': '7BAG',
            'QUEUE_PREVIEWS': 5,
            'SEED': 0,
            'HOLD_ENABLED': True,
            'ALLOWED_SPINS': 'ALL-MINI',
            'LOCK_OUT_OK': True,
            'TOP_OUT_OK': False,
            'RESET_ON_TOP_OUT': False
        }
               
    def __initalise(self):
        set_flag_attr()
        
        self.input_thread = threading.Thread(target = self.InputManager.input_loop)
        self.logic_thread = threading.Thread(target = self.GameInstanceManager.logic_loop)
        
    def __register_event_handlers(self):
        # window focus events
        PygameEventHandler.register(pygame.WINDOWCLOSE)(self.__exit)
        PygameEventHandler.register(pygame.WINDOWFOCUSLOST)(self.__is_focused)
        PygameEventHandler.register(pygame.WINDOWFOCUSGAINED)(self.__is_focused)
        PygameEventHandler.register(pygame.VIDEOEXPOSE)(self.__is_focused)
        PygameEventHandler.register(pygame.WINDOWMINIMIZED)(self.__is_focused)
        PygameEventHandler.register(pygame.WINDOWRESTORED)(self.__is_focused)
        PygameEventHandler.register(pygame.WINDOWENTER)(self.__is_focused)
        PygameEventHandler.register(pygame.WINDOWLEAVE)(self.__is_focused)
        PygameEventHandler.register(pygame.WINDOWSHOWN)(self.__is_focused)
        PygameEventHandler.register(pygame.WINDOWHIDDEN)(self.__is_focused)
       
        # window resize events
        PygameEventHandler.register(pygame.WINDOWRESIZED)(self.__handle_window_resize)

        # mouse events
        PygameEventHandler.register(pygame.MOUSEBUTTONDOWN)(self.MouseInputHandler.on_mouse_down)
        PygameEventHandler.register(pygame.MOUSEBUTTONUP)(self.MouseInputHandler.on_mouse_up)
        PygameEventHandler.register(pygame.MOUSEMOTION)(self.MouseInputHandler.on_mouse_move)
        PygameEventHandler.register(pygame.MOUSEWHEEL)(self.MouseInputHandler.on_mouse_scroll)
        
    def __init_pygame(self):
        pygame.init()
        pygame.font.init()
        
        pygame.event.set_allowed([
            pygame.QUIT,
            pygame.ACTIVEEVENT,
            pygame.VIDEORESIZE,
            pygame.VIDEOEXPOSE,
            pygame.WINDOWCLOSE,
            pygame.WINDOWMAXIMIZED,
            pygame.WINDOWMINIMIZED,
            pygame.WINDOWRESIZED,
            pygame.WINDOWRESTORED,
            pygame.WINDOWENTER,
            pygame.WINDOWLEAVE,
            pygame.WINDOWSHOWN,
            pygame.WINDOWHIDDEN,
            pygame.WINDOWFOCUSLOST,
            pygame.WINDOWFOCUSGAINED,
            pygame.CLIPBOARDUPDATE,
            pygame.DROPFILE,
            pygame.DROPBEGIN,
            pygame.DROPCOMPLETE,
            pygame.TEXTINPUT,
            pygame.TEXTEDITING,
            pygame.MOUSEBUTTONUP, # mouse events are for UI, which will happen on a frame basis
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEMOTION,
            pygame.MOUSEWHEEL,
            ]
        )
        
    def run(self):
        self.__initalise()
         
        self.InputManager.start_keyboard_hook() 
        self.Timing.start_times['input_loop'] = time.perf_counter()
        self.input_thread.start()
        
        self.Timing.start_times['logic_loop'] = time.perf_counter()
        self.logic_thread.start()
        
        self.Timing.start_times['render_loop'] = time.perf_counter()
        self.render_loop() # render loop has to be in main thread because calling pygame events in a seperate thread isn't allowed in macOS, stupid as fuck

        self.__exit()
             
    def __exit(self, event = None):
        self.Timing.exited = True
        self.InputManager.exit()
        pygame.font.quit()
        pygame.quit()
        
        if self.input_thread.is_alive():
            self.input_thread.join(timeout = self.Timing.poll_interval)

        if self.logic_thread.is_alive():
            self.logic_thread.join(timeout = self.Timing.tick_interval)

        os._exit(0)
              
    def render_loop(self):
        """
        Render loop handles frame based updates, so drawing frames and the UI logic and handle window events.
        Tick rate is as a fast as possible.
        """
        try:
            while not self.Timing.exited:

                self.Timing.current_frame_time = time.perf_counter() - self.Timing.start_times['render_loop']
                self.Timing.elapsed_times['render_loop'] = self.Timing.current_frame_time
                
                self.Timing.frame_delta_time = (self.Timing.current_frame_time - self.Timing.last_frame_time)
                self.Timing.last_frame_time = self.Timing.current_frame_time
                  
                self.do_render_tick()
                self.get_fps()
                time.sleep(0)
                        
        except Exception as e:
            print(f"\033[91mError in {threading.current_thread().name}: {e}\033[0m")
            return
        
        finally: 
            if self.PRINT_WARNINGS:
                print(f"\033[92mRender loop Timing.exited in {threading.current_thread().name}\033[0m")  
            self.Timing.exited = True
            return
                
    def do_render_tick(self):
        
        start = time.perf_counter()
       
        if self.Timing.exited:
            return
        
        for event in pygame.event.get():
            PygameEventHandler.notify(event)
        
        self.__update_mouse_position()
        self.MenuInputHandler.tick()
        self.MenuManager.tick()
        self.Debug.get_metrics()  
        self.Render.draw_frame()
        self.FrameClock.tick()

        self.Timing.iteration_times['render_loop'] = time.perf_counter() - start
                 
    def get_fps(self):
        self.Timing.FPS = self.FrameClock.get_fps()
    
    def __is_focused(self, event):
        match event.type:
            case pygame.WINDOWFOCUSGAINED:
                self.is_focused = True
            case pygame.WINDOWFOCUSLOST:
                self.is_focused = False
            case pygame.VIDEOEXPOSE:
                self.is_focused = True
            case pygame.WINDOWMINIMIZED:
                self.is_focused = False
        
        self.MenuManager.is_focused = self.is_focused
        self.MouseInputHandler.is_focused = self.is_focused
        self.Timing.is_focused = self.MenuManager.is_focused
    
    def __update_mouse_position(self):
        self.MenuManager.mouse_position = self.MouseInputHandler.Mouse.position
    
    def __handle_window_resize(self, event):
       self.Render.handle_window_resize()    
class GameInstance():
    def __init__(self, ID, Config, TimingStruct, HandlingConfig, GameParameters):
        
        self.ID = ID
        self.Config = Config
        self.GameParameters = GameParameters
        
        self.TimingStruct = TimingStruct
        
        self.HandlingConfig = HandlingConfig
        self.HandlingStruct = StructHandling()
        
        self.FlagStruct = StructFlags()
        self.GameInstanceStruct = StructGameInstance()
        
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

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()