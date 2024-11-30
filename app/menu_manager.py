from render.GUI.menu import Menu
from app.menu_kb_input_handler import UIAction

class MenuManager():
    def __init__(self, menu_actions_queue, Config, Timing):
        
        self.menu_actions_queue = menu_actions_queue
        self.Config = Config
        self.Timing = Timing
        self.debug_overlay = False
    
    def init_menus(self, window):
        self.window = window
        
        self.home_menu           = Menu(self.window, self.Config, self.Timing, menu_definition = 'render/GUI/menus/home_menu.json')
        self.solo_menu           = Menu(self.window, self.Config, self.Timing, menu_definition = 'render/GUI/menus/solo_menu.json')
        self.multi_menu          = Menu(self.window, self.Config, self.Timing, menu_definition = 'render/GUI/menus/multi_menu.json')
        self.records_menu        = Menu(self.window, self.Config, self.Timing, menu_definition = 'render/GUI/menus/records_menu.json')
        self.about_menu          = Menu(self.window, self.Config, self.Timing, menu_definition = 'render/GUI/menus/about_menu.json')
        self.config_menu         = Menu(self.window, self.Config, self.Timing, menu_definition = 'render/GUI/menus/config_menu.json')
        
        self.current_menu = self.home_menu
        
    def tick(self):
        self.get_actions()
        self.current_menu.update()
    
    def get_actions(self):
        actions = self.menu_actions_queue.get_nowait()
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