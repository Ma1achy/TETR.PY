from render.GUI.menu import Menu
from app.menu_kb_input_handler import UIAction
from render.GUI.debug_overlay import GUIDebug
from render.GUI.focus_overlay import GUIFocus
from render.GUI.diaglog_box import DialogBox
import webbrowser
from utils import copy2clipboard
class MenuManager():
    def __init__(self, Keyboard, Mouse, Config, Timing, RenderStruct, Debug):

        self.Keyboard = Keyboard
        self.Mouse = Mouse
        self.Config = Config
        self.Timing = Timing
        self.RenderStruct = RenderStruct
        self.Debug = Debug
        
        self.debug_overlay = False
        self.show_error_dialog = False
        self.is_focused = False
        
        self.GUI_debug = GUIDebug(self.Config, self.RenderStruct, self.Debug)
        self.GUI_focus = GUIFocus(self.RenderStruct)
        self.ErrorDialog = None
            
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
        self.ExitDialog = DialogBox(self.Timing, self.window, self.Mouse, self.RenderStruct, title = 'EXIT TETR.PY?', message = None , buttons = ['CANCEL', 'EXIT'], funcs = [self.close_dialog, self.quit_game], click_off_dissmiss = True, width = 500)
         
        self.home_menu           = Menu(self.window, self.Config, self.Timing, self.Mouse, self.button_functions, menu_definition = 'render/GUI/menus/home_menu.json')
        self.solo_menu           = Menu(self.window, self.Config, self.Timing, self.Mouse, self.button_functions, menu_definition = 'render/GUI/menus/solo_menu.json')
        self.multi_menu          = Menu(self.window, self.Config, self.Timing, self.Mouse, self.button_functions, menu_definition = 'render/GUI/menus/multi_menu.json')
        self.records_menu        = Menu(self.window, self.Config, self.Timing, self.Mouse, self.button_functions, menu_definition = 'render/GUI/menus/records_menu.json')
        self.about_menu          = Menu(self.window, self.Config, self.Timing, self.Mouse, self.button_functions, menu_definition = 'render/GUI/menus/about_menu.json')
        self.config_menu         = Menu(self.window, self.Config, self.Timing, self.Mouse, self.button_functions, menu_definition = 'render/GUI/menus/config_menu.json')
        self.button_functions, 
        self.current_menu = self.home_menu
        
        self.in_dialog = False
        self.current_dialog = None
    
    def tick(self):
        self.get_actions()
        self.handle_exceptions()
        
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
        if self.in_dialog:
            if self.current_dialog.primary_button is None:
                return
            self.current_dialog.primary_button.click()
        else:
            self.current_menu.main_body.back_button.click()
    
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
        self.ExitDialog.handle_window_resize()
        
        if self.current_dialog:
            self.current_dialog.handle_window_resize()
    
    def go_to_exit(self):
        self.current_menu.reset_buttons()
        self.in_dialog = True
        self.current_dialog = self.ExitDialog
    
    def quit_game(self):
        self.Timing.exited = True
    
    def copy_to_clipboard(self, item):
        self.current_dialog.reset_buttons()
        copy2clipboard(item)
        
    def close_dialog(self):
        self.current_dialog.reset_buttons()
        self.in_dialog = False
        self.current_dialog = None
        self.ErrorDialog = None
    
    def open_error_dialog(self):
        if not self.show_error_dialog:
            return
        
        self.show_error_dialog = False
        self.current_menu.reset_buttons()
        self.in_dialog = True
             
    def go_to_home(self):
        self.current_menu.reset_buttons()
        self.current_menu = self.home_menu
    
    # home menu
    
    def go_to_multi(self):
        self.current_menu.reset_buttons()
        self.current_menu = self.multi_menu
    
    def go_to_solo(self):
        self.current_menu.reset_buttons()
        self.current_menu = self.solo_menu
    
    def go_to_records(self): 
        self.current_menu.reset_buttons()
        self.current_menu = self.records_menu
    
    def go_to_config(self):
        self.current_menu.reset_buttons()
        self.current_menu = self.config_menu
    
    def go_to_about(self):
        self.current_menu.reset_buttons()
        self.current_menu = self.about_menu
    
    def go_to_github(self):
        self.current_menu.reset_buttons()
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
    
    def handle_exceptions(self):
        self.__create_error_message_dialog()
        self.open_error_dialog()
        
    def __create_error_message_dialog(self): 
        if self.Debug.ERROR is None:
            return
        
        info, error, trace = self.Debug.ERROR
        self.current_dialog = DialogBox(self.Timing, self.window, self.Mouse, self.RenderStruct, title = 'UH OH . . .', message = f"TETR.PY has encountered a problem!\n [colour=#FF0000]{error}[/colour]\n \n [colour=#BBBBBB]{trace}[/colour]\nPlease report this problem at: \n https://github.com/Ma1achy/TETR.PY/issues", buttons = ['DISMISS', 'COPY'], funcs = [self.close_dialog, lambda: self.copy_to_clipboard(info)], click_off_dissmiss = True, width = 700)
        
        self.show_error_dialog = True
        self.Debug.ERROR = None
    
    