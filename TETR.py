import threading
from app.state.config import Config
import time
from instance.handling.handling_config import HandlingConfig
from app.debug.debug_metrics import DebugMetrics
from instance.state.flags import set_flag_attr
from render.render_new import StructRender
from app.state.clock import Clock
import pygame
import os
from render.render_new import Render
from app.input.keyboard.keyboard_input_manager import KeyboardInputManager
from app.core.game_instance_manager import GameInstanceManager
from app.input.keyboard.menu_kb_input_handler import MenuKeyboardInputHandler, UIAction
from app.debug.debug_manager import DebugManager
from app.core.pygame_event_handler import PygameEventHandler
from app.state.timing import Timing
from app.core.menu_manager import MenuManager
from app.input.mouse.mouse_input_handler import MouseInputManager
from app.input.keyboard.keyboard import Keyboard
from app.input.mouse.mouse import Mouse
import logging
import traceback
import datetime
import sys
import json
import pkg_resources

logging.basicConfig(level = logging.ERROR, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class App():
    def __init__(self):
        
        self.is_focused = False
        self.game_instances = []
        
        self.Keyboard = Keyboard()
        self.Mouse = Mouse()
        
        self.Config = Config()    
        self.Timing = Timing()
        self.FrameClock = Clock()
        
        self.RenderStruct = StructRender()
        self.DebugStruct = DebugMetrics()
        self.HandlingConfig = HandlingConfig()
        
        self.DebugStruct.PRINT_WARNINGS = True
        
        self.KeyboardInputManager = KeyboardInputManager(self.Keyboard, self.Timing, self.DebugStruct)
        self.MouseInputManager = MouseInputManager(self.Mouse)
        
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
   
        self.MenuInputHandler = MenuKeyboardInputHandler(self.Keyboard, self.menu_key_bindings, self.Timing)
        self.MenuManager = MenuManager(self.Keyboard, self.Mouse, self.Config, self.Timing, self.RenderStruct, self.DebugStruct)
        self.GameInstanceManager = GameInstanceManager(self.Timing, self.DebugStruct)
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
        
        self.input_thread = threading.Thread(target = self.KeyboardInputManager.input_loop)
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
        PygameEventHandler.register(pygame.MOUSEBUTTONDOWN)(self.MouseInputManager.on_mouse_down)
        PygameEventHandler.register(pygame.MOUSEBUTTONUP)(self.MouseInputManager.on_mouse_up)
        PygameEventHandler.register(pygame.MOUSEMOTION)(self.MouseInputManager.on_mouse_move)
        PygameEventHandler.register(pygame.MOUSEWHEEL)(self.MouseInputManager.on_mouse_scroll)
        
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
         
        self.KeyboardInputManager.start_keyboard_hook() 
        self.Timing.start_times['input_loop'] = time.perf_counter()
        self.input_thread.start()
        
        self.Timing.start_times['logic_loop'] = time.perf_counter()
        self.logic_thread.start()
        
        self.Timing.start_times['render_loop'] = time.perf_counter()
        self.render_loop() # render loop has to be in main thread because calling pygame events in a seperate thread isn't allowed in macOS, stupid as fuck

        self.__exit()
             
    def __exit(self, event = None):
        self.Timing.exited = True
        self.KeyboardInputManager.exit()
        pygame.font.quit()
        pygame.quit()
        
        if self.input_thread.is_alive():
            self.input_thread.join(timeout = self.Timing.poll_interval)


        if self.logic_thread.is_alive():
            self.logic_thread.join(timeout = self.Timing.tick_interval)

        os._exit(0)
    
    def restart(self, error):  # if main thread crashes, attempt to restart entire program
        self.Timing.restarts += 1
        current_time = time.perf_counter()
    
        time_since_last_restart = current_time - self.Timing.last_restart_time
       
        if time_since_last_restart < self.Timing.restart_interval :
            print(f"\033[91mRestart attempt too soon! \nExiting program... \nLast error: \n{error}\033[0m")
            self.__exit()
            return
        
        self.Timing.last_restart_time = current_time
        print('\033[93mAttempting restart:\033[0m')
        self.DebugStruct.ERROR = error
        
        try:
            self.run()
        except Exception as e:
            print(f"\033[93mError during restart attempt: {e}\033[0m")
            self.restart(e)
            
    def render_loop(self):
        """
        Render loop handles frame based updates, so drawing frames and the UI logic and handle window events.
        Tick rate is as a fast as possible.
        """
        if self.DebugStruct.PRINT_WARNINGS and self.Timing.restarts != 0:
            print(f"\033[93mRestarting {threading.current_thread().name}...\033[0m")
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
            self.handle_exception(e)
        
        finally: 
            if self.DebugStruct.PRINT_WARNINGS:
                print(f"\033[92mRender loop Timing exited in {threading.current_thread().name}\033[0m")  
            return
                
    def do_render_tick(self):
        
        start = time.perf_counter()
       
        if self.Timing.exited:
            return
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.WINDOWCLOSE: # stop the window close event from being processed by pygame
                self.__window_close_event(event)
                return
                
            PygameEventHandler.notify(event)
        
        self.__update_mouse_position()
        self.MenuInputHandler.tick()
        self.MenuManager.tick()
        self.Debug.get_metrics()  
        self.Render.draw_frame()
        self.FrameClock.tick()
        
        while not self.Mouse.events.empty():
            self.Mouse.events.get_nowait()

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
        self.MouseInputManager.is_focused = self.is_focused
        self.Timing.is_focused = self.MenuManager.is_focused
    
    def __update_mouse_position(self):
        self.MenuManager.mouse_position = self.MouseInputManager.Mouse.position
    
    def __handle_window_resize(self, event):
       self.Render.handle_window_resize()
    
    def __window_close_event(self, event):
        self.MenuManager.go_to_exit()
    
    def handle_exception(self, e):
        print(f"\033[91mError in {threading.current_thread().name}: \n{e}\033[0m")
        
        tb_str = traceback.format_exc()
        current_thread = threading.current_thread()
        timestamp = datetime.datetime.now().isoformat()
        
        env_info = {
            "OS": os.name,
            "Platform": sys.platform,
            "Python Version": sys.version,
            "Current Working Directory": os.getcwd(),
            "Imported Packages": self.__get_imported_packages(),
            "Build Info": self.__get_build_info()
        }
        
        logging.error(f"\033[91mException occurred at {timestamp} in thread {current_thread.name}:\n{tb_str}\033[0m")
        logging.error("Environment information: %s", env_info)
        
        info = {
            "Exception Information": {
            "Timestamp": timestamp,
            "Thread": current_thread.name,
            "Traceback": tb_str
            },
            
            "Environment Information": env_info
        }
        self.restart((info, e, tb_str))
    
    def __get_imported_packages(self):
        imported_packages = {}
        for name, module in sys.modules.items():
            if name in pkg_resources.working_set.by_key:
                imported_packages[name] = pkg_resources.working_set.by_key[name].version
        return imported_packages

    def __get_build_info(self):
        path = os.path.join(os.getcwd(), 'app/state/build_info.json')
        try:
            with open(path, 'r') as file:
                build_info = json.load(file)
        except Exception as _:
            build_info = None
        return build_info

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()