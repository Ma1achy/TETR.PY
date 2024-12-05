from render.GUI.menu import Menu
from app.menu_kb_input_handler import UIAction
from render.GUI.debug_overlay import GUIDebug
from render.GUI.focus_overlay import GUIFocus
import webbrowser

class MenuManager():
    def __init__(self, Keyboard, Mouse, Config, Timing, RenderStruct, Debug):

        self.Keyboard = Keyboard
        self.Mouse = Mouse
        self.Config = Config
        self.Timing = Timing
        self.RenderStruct = RenderStruct
        self.Debug = Debug
        
        self.debug_overlay = False
        self.is_focused = False
        
        self.GUI_debug = GUIDebug(self.Config, self.RenderStruct, self.Debug)
        self.GUI_focus = GUIFocus(self.RenderStruct)
        
        self.button_functions = {
            "go_to_exit": self.go_to_exit,
            "go_to_home": self.go_to_home,
            
            # home menu
            "go_to_multi": self.go_to_multi,
            "go_to_solo": self.go_to_solo,
            "go_to_records": self.go_to_records,
            "go_to_config": self.go_to_config,
            "go_to_about": self.go_to_about,
            "go_to_github": self.go_to_github,
            
            # solo menu
            "go_to_40_lines": self.go_to_40_lines,
            "go_to_blitz": self.go_to_blitz,
            "go_to_zen": self.go_to_zen,
            "go_to_custom": self.go_to_custom,
    }
    
    def init_menus(self, window):
        self.window = window
        
        self.home_menu           = Menu(self.window, self.Config, self.Timing, self.Mouse, self.Keyboard, self.button_functions, menu_definition = 'render/GUI/menus/home_menu.json')
        self.solo_menu           = Menu(self.window, self.Config, self.Timing, self.Mouse, self.Keyboard, self.button_functions, menu_definition = 'render/GUI/menus/solo_menu.json')
        self.multi_menu          = Menu(self.window, self.Config, self.Timing, self.Mouse, self.Keyboard, self.button_functions, menu_definition = 'render/GUI/menus/multi_menu.json')
        self.records_menu        = Menu(self.window, self.Config, self.Timing, self.Mouse, self.Keyboard, self.button_functions, menu_definition = 'render/GUI/menus/records_menu.json')
        self.about_menu          = Menu(self.window, self.Config, self.Timing, self.Mouse, self.Keyboard, self.button_functions, menu_definition = 'render/GUI/menus/about_menu.json')
        self.config_menu         = Menu(self.window, self.Config, self.Timing, self.Mouse, self.Keyboard, self.button_functions, menu_definition = 'render/GUI/menus/config_menu.json')
        self.button_functions, 
        self.current_menu = self.home_menu
        
    def tick(self):
        self.get_actions()
 
    def get_actions(self):
        actions = self.Keyboard.menu_actions_queue.get_nowait()
        self.__perform_action(actions)
        
    def __perform_action(self, actions):

        for action in actions:
            match action:
                case UIAction.MENU_LEFT:
                    self.__menu_left()
                case UIAction.MENU_RIGHT:
                    self.__menu_right()
                case UIAction.MENU_UP:
                    self.__menu_up()
                case UIAction.MENU_DOWN:
                    self.__menu_down()
                case UIAction.MENU_CONFIRM:
                    self.__menu_confirm()
                case UIAction.MENU_BACK:
                    self.__menu_back()
                case UIAction.MENU_DEBUG:
                    self.__menu_debug()
                case UIAction.WINDOW_FULLSCREEN:
                    self.RenderStruct.fullscreen = not self.RenderStruct.fullscreen
         
    def __menu_left(self):
        pass
    
    def __menu_right(self):
        pass
    
    def __menu_up(self):
        pass

    def __menu_down(self):
        pass
    
    def __menu_confirm(self):
        pass
    
    def __menu_back(self):
        pass
    
    def __menu_debug(self):
        self.debug_overlay = not self.debug_overlay
    
    def handle_window_resize(self):
        self.home_menu.handle_window_resize()
        self.solo_menu.handle_window_resize()
        self.multi_menu.handle_window_resize()
        self.records_menu.handle_window_resize()
        self.about_menu.handle_window_resize()
        self.config_menu.handle_window_resize()
        self.GUI_debug.handle_window_resize()
        self.GUI_focus.handle_window_resize()
    
    def go_to_exit(self):
        pass
    
    def go_to_home(self):
        self.current_menu = self.home_menu
    
    # home menu
    
    def go_to_multi(self):
        self.current_menu = self.multi_menu
    
    def go_to_solo(self):
        self.current_menu = self.solo_menu
    
    def go_to_records(self): 
        self.current_menu = self.records_menu
    
    def go_to_config(self):
        self.current_menu = self.config_menu
    
    def go_to_about(self):
        self.current_menu = self.about_menu
    
    def go_to_github(self):
        webbrowser.open('https://github.com/Ma1achy/TETR.PY')
    
    # solo menu
    
    def go_to_40_lines(self):
        pass
    
    def go_to_blitz(self):
        pass
    
    def go_to_zen(self):
        pass
    
    def go_to_custom(self):
        pass
    