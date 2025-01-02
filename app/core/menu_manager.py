from render.GUI.menu import Menu
from render.GUI.font import Font
from app.input.keyboard.menu_kb_input_handler import UIAction
from render.GUI.debug_overlay import GUIDebug
from render.GUI.focus_overlay import GUIFocus
from render.GUI.diaglog_box import DialogBox
import webbrowser
from utils import copy2clipboard, smoothstep, TransformSurface
import pygame
from render.GUI.menu_elements.text_input import TextInput

class MenuManager():
    def __init__(self, Keyboard, Mouse, Timing, RenderStruct, Debug, pygame_events_queue, AccountManager, ConfigManager):
        """
        The menu manager, manages the current menu and GUI elements and transitions
        
        args:
            Keyboard (Keyboard): The Keyboard object
            Mouse (Mouse): The Mouse object
            Timing (Timing): The Timing object
            RenderStruct (StructRender): The RenderStruct object
            Debug (Debug): The Debug object
            pygame_events_queue (queue): The pygame events queue
            AccountManager (AccountManager): The AccountManager object
            ConfigManager (ConfigManager): The ConfigManager object
        """
        self.Keyboard = Keyboard
        self.Mouse = Mouse
        self.Timing = Timing
        self.RenderStruct = RenderStruct
        self.Debug = Debug
        self.pygame_events_queue = pygame_events_queue
        
        self.AccountManager = AccountManager
        self.ConfigManager = ConfigManager
        
        self.debug_overlay = False
        self.is_focused = False
        self.in_dialog = False
        self.wait_for_dialog_close = False
        
        self.ErrorDialog = None
            
        self.button_functions = {
            "go_to_exit": self.open_exit_dialog,
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
            
            "go_to_account_settings": self.go_to_account_settings,
            "export_settings": self.export_settings,
            "open_logout_dialog": self.open_logout_dialog
    }
        
        self.render_copied_text()
        
        self.copied_failed = False
        self.do_copy_to_clipboard_animation = False
        self.copy_text_do_fade_out = False
        self.copied_text_animation_length = 0.5
        self.copied_text_timer = 0
        
        self.darken_overlay_layer_alpha = 0
        
    def init_menus(self, window):
        """
        Initialise the menus and GUI elements
        
        args:
            window (pygame.Surface): The window to draw the menus on
        """
        self.window = window
        self.darken_overlay = pygame.Surface((self.RenderStruct.RENDER_WIDTH, self.RenderStruct.RENDER_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)
        self.darken_overlay.fill((0, 0, 0))
        
        self.GUI_debug = GUIDebug(self.window, self.Timing, self.RenderStruct, self.Debug)
        self.GUI_focus = GUIFocus(self.window, self.RenderStruct)
        
        self.LoginDialog = DialogBox(
            self.Timing, 
            self.window, 
            self.Mouse, 
            self.RenderStruct, 
            title = 'WELCOME TO TETR.PY', 
            message = "Enter a username to login" ,
            buttons = ['LOGIN'], 
            funcs = [lambda: self.login(self.LoginDialog.TextEntry.get_value())], 
            click_off_dissmiss = False, 
            width = 550, 
            
            TextEntry = TextInput(
                allowed_input = 'alphanumeric',
                no_empty_input = True,
                max_chars = 32,
                force_caps = True,
                font_colour = '#ffffff',
                cursor_colour = '#ffffff',
                font_type = 'hun2.ttf',
                font_size = 25,
                pygame_events_queue = self.pygame_events_queue,
                function = self.login,
                RENDER_SCALE = self.RenderStruct.RENDER_SCALE
            )
        )
        
        self.ExitDialog = DialogBox(
            self.Timing,
            self.window,
            self.Mouse,
            self.RenderStruct,
            title = 'EXIT TETR.PY?',
            message = None ,
            buttons = ['CANCEL', 'EXIT'],
            funcs = [self.close_dialog, self.quit_game],
            click_off_dissmiss = True,
            width = 500
        )
        
        self.LogOutDialog = DialogBox(
            self.Timing,
            self.window,
            self.Mouse,
            self.RenderStruct,
            title = 'LOGOUT?',
            message = None,
            buttons = ['CANCEL', 'LOGOUT'],
            funcs = [self.close_dialog, self.logout],
            click_off_dissmiss = True,
            width = 500
        )
        
        self.login_menu          = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/login_menu.json')
        self.home_menu           = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/home_menu.json')
        self.solo_menu           = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/solo_menu.json')
        self.multi_menu          = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/multi_menu.json')
        self.records_menu        = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/records_menu.json')
        self.about_menu          = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/about_menu.json')
        self.config_menu         = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/config_menu.json')

        self.account_menu        = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/account_menu.json')

        self.forty_lines_menu    = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/40_lines_menu.json')
        self.blitz_menu          = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/blitz_menu.json')
        self.zen_menu            = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/zen_menu.json')
        self.custom_solo_menu    = Menu(self.window, self.Timing, self.Mouse, self.RenderStruct, self.button_functions, menu_definition = 'render/GUI/menus/custom_solo_menu.json')
        
        self.current_menu = self.home_menu
        self.next_menu = None
        self.previous_menu = None

        self.current_dialog = None
        self.dialog_stack = []  
        
    def tick(self):
        """
        Update the menus and GUI elements
        """
        self.darken_overlay.fill((0, 0, 0, 200))
        self.window.blit(self.darken_overlay, (0, 0))
        
        if self.current_menu is not None:
            self.current_menu.update(self.in_dialog)
             
        if self.current_dialog:
            self.darken_overlay.fill((0, 0, 0, self.darken_overlay_layer_alpha))
            self.window.blit(self.darken_overlay, (0, 0))
            self.current_dialog.update()
            
        self.copy_to_clipboard_animation()
        
        if self.debug_overlay:
            self.GUI_debug.update()
        
        if not self.is_focused:
            self.GUI_focus.update()
              
        self.__wait_for_dialog_close()
        self.update_darken_overlay_alpha()
        self.reset_dialogs()
        self.get_actions()
        self.handle_exceptions()
        self.handle_menu_transitions()
        
    def if_doing_animation(self):
        """
        Check if the current menu is doing an animation
        """
        if self.current_menu.doing_transition_animation:
            return True
        
        if self.current_dialog is not None:
            if self.current_dialog.do_animate_appear or self.current_dialog.do_animate_disappear:
                return True
        
        return False
        
    def get_actions(self):
        """
        Get the actions from the keyboard input handler
        """
        actions = self.Keyboard.menu_actions_queue.get_nowait()
        self.__perform_action(actions)

    def __perform_action(self, actions):
        """
        Perform the actions from the keyboard input handler
        
        args:
            actions (list): The list of actions to perform
        """
        if self.if_doing_animation(): # ignore input events if doing a menu transition animation
            return
        
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
        """
        Go back to the previous menu or close the current dialog
        """
        if self.in_dialog:
            if self.current_dialog.primary_button is None:
                return
            self.current_dialog.primary_button.click()
        else:
            self.current_menu.main_body.back_button.click()
    
    def __menu_debug(self):
        """
        Toggle the debug overlay
        """
        self.debug_overlay = not self.debug_overlay
    
    def handle_window_resize(self):
        """
        Handle the window resize
        """
        self.darken_overlay = pygame.Surface((self.RenderStruct.WINDOW_WIDTH, self.RenderStruct.WINDOW_HEIGHT), pygame.SRCALPHA|pygame.HWSURFACE)
        
        self.login_menu.handle_window_resize()
        self.home_menu.handle_window_resize()
        self.solo_menu.handle_window_resize()
        self.multi_menu.handle_window_resize()
        self.records_menu.handle_window_resize()
        self.about_menu.handle_window_resize()
        self.config_menu.handle_window_resize()
        
        self.account_menu.handle_window_resize()
        
        self.forty_lines_menu.handle_window_resize()
        self.blitz_menu.handle_window_resize()
        self.zen_menu.handle_window_resize()
        self.custom_solo_menu.handle_window_resize()
        
        self.GUI_debug.handle_window_resize()
        self.GUI_focus.handle_window_resize()
        self.ExitDialog.handle_window_resize()
        self.LogOutDialog.handle_window_resize()
        self.LoginDialog.handle_window_resize()
        
        if self.ErrorDialog:
            self.ErrorDialog.handle_window_resize()
        
        if self.current_dialog:
            self.current_dialog.handle_window_resize()
        
        self.copied_text_surface_rect = pygame.Rect((self.RenderStruct.WINDOW_WIDTH - self.copied_text_surface_width)//2, (self.RenderStruct.WINDOW_HEIGHT - self.copied_text_surface_height)//2, self.copied_text_surface_width, self.copied_text_surface_height)
    
    def go_to_login(self):
        """
        Go to the login menu
        """
        self.dialog_stack.clear()
        self.current_dialog = None
        self.in_dialog = False

        self.current_menu.reset_state()
        self.current_menu = self.login_menu
        self.open_dialog(self.LoginDialog)

    # login dialog
    def login(self, value):
        """
        Login to the account
        
        args:
            value (str): The username to login with
        """
        self.current_dialog.reset_state()
        self.current_dialog.TextEntry.manager.value = ""
        self.AccountManager.login(value)
        self.close_dialog()
        self.switch_menus(self.home_menu)

    # logout dialog
    def open_logout_dialog(self):
        """
        Open the logout dialog
        """
        self.current_menu.reset_state()
        self.open_dialog(self.LogOutDialog)
    
    def logout(self):
        """
        Logout of the account
        """
        self.current_dialog.reset_state()
        self.close_dialog()

        # Reset dialog states
        self.dialog_stack.clear()
        self.current_dialog = None
        self.in_dialog = False

        self.AccountManager.logout()
        self.go_to_login()
 
    # exit dialog
    
    def open_exit_dialog(self):
        """
        Open the exit dialog
        """
        self.current_menu.reset_state()
        self.open_dialog(self.ExitDialog)
    
    def quit_game(self):
        """
        Quit the game
        """
        self.Timing.exited = True
    
    # copy to clipboard
    
    def copy_to_clipboard(self, item):
        """
        Copy the item to the clipboard
        """
        self.current_dialog.reset_state()
        try:
            copy2clipboard(item)
            self.do_copy_to_clipboard_animation = True
            
        except Exception as _:
            self.handle_copy_to_clipboard_fail()
            
    def handle_copy_to_clipboard_fail(self):
        """
        Handle the copy to clipboard failure
        """
        self.copied_text_surface.fill((0, 0, 0, 0))
            
        self.copied_text.draw(self.copied_text_surface, 'COPY FAILED!', '##AB0000', 'center', 0, 5)
        self.copied_text.draw(self.copied_text_surface, 'COPY FAILED!', '#FF0000', 'center', 0, 0)
        
        self.do_copy_to_clipboard_animation = True
        self.copied_failed = True
            
    def copy_to_clipboard_animation(self):
        """
        Animate the copy to clipboard text
        """
        if not self.do_copy_to_clipboard_animation:
            return
        
        self.copied_text_timer += self.Timing.frame_delta_time
        
        if not self.copy_text_do_fade_out:
            if self.copied_text_timer >= self.copied_text_animation_length:
                self.copy_text_do_fade_out = True
                self.copied_text_timer = 0
            
            self.copied_text_alpha = min(255, smoothstep(self.copied_text_timer / self.copied_text_animation_length) * 255)
            self.copied_text_surface.set_alpha(self.copied_text_alpha)
            
            animation_surface = TransformSurface(self.copied_text_surface, max(0, smoothstep(self.copied_text_timer / self.copied_text_animation_length)), 0, pygame.Vector2(self.copied_text_surface_rect.width//2, self.copied_text_surface_rect.height//2), pygame.Vector2(self.RenderStruct.WINDOW_WIDTH//2, self.RenderStruct.WINDOW_HEIGHT//2), pygame.Vector2(0, 0))
            self.window.blit(animation_surface[0], animation_surface[1].topleft)
        
        else:
            if self.copied_text_timer >= self.copied_text_animation_length * 5:
                self.reset_copy_to_clipboard_animation()
                return
            
            self.copied_text_alpha = 255 - min(255, (self.copied_text_timer / (self.copied_text_animation_length * 5) ) * 255)
            self.copied_text_surface.set_alpha(self.copied_text_alpha)
            
            self.window.blit(self.copied_text_surface, self.copied_text_surface_rect.topleft)
        
    def reset_copy_to_clipboard_animation(self):
        """
        Reset the copy to clipboard animation
        """
        self.do_copy_to_clipboard_animation = False
        self.copy_text_do_fade_out = False
        self.copied_text_timer = 0
        self.copied_text_alpha = 0
        self.copied_text_surface.set_alpha(self.copied_text_alpha)
        
        if self.copied_failed:
            self.copied_failed = False
            self.copied_text_surface.fill((0, 0, 0, 0))
            self.copied_text.draw(self.copied_text_surface, 'COPIED TO CLIPBOARD!', '#FF7B10', 'center', 0, 5)
            self.copied_text.draw(self.copied_text_surface, 'COPIED TO CLIPBOARD!', '#FFD800', 'center', 0, 0)
    
    # dialog boxes
           
    def open_dialog(self, dialog):
        """
        Opens a new dialog box and animates it.
        
        args:
            dialog (DialogBox): The dialog box to open
        """
        if not dialog:
            return  

        if self.current_dialog == dialog:
            return
    
        if self.current_dialog and self.current_dialog != dialog:
            if self.current_dialog not in self.dialog_stack:
                self.dialog_stack.append(self.current_dialog) 
                
            self.current_dialog.do_animate_disappear = True
            self.current_dialog.do_animate_appear = False  
            self.current_dialog.timer = 0

        self.current_dialog = dialog
        self.in_dialog = True
        
        if self.current_menu:
            self.current_menu.reset_state()

        dialog.do_animate_appear = True
        dialog.do_animate_disappear = False
        dialog.timer = 0

    def close_dialog(self):
        """
        Closes the current dialog and animates the previous dialog (if any).
        """
        if not self.current_dialog:
            return

        self.current_dialog.reset_state()
        self.current_dialog.do_animate_disappear = True
        self.current_dialog.do_animate_appear = False
        self.current_dialog.timer = 0
        self.wait_for_dialog_close = True

    def reset_dialogs(self):
        """
        Resets dialogs and ensures animation states are consistent.
        """
        if self.current_dialog and self.current_dialog.closed:
            self.current_dialog.closed = False
            self.current_dialog.do_animate_appear = True
            self.current_dialog.do_animate_disappear = False
            self.current_dialog.timer = 0

        for dialog in self.dialog_stack:
            if dialog.closed:
                dialog.closed = False
                dialog.do_animate_appear = True
                dialog.do_animate_disappear = False
                dialog.timer = 0
    
    def __wait_for_dialog_close(self):
        """
        Waits for the current dialog to close before proceeding to the previous one in the stack.
        """
        if self.current_dialog is None:
            return

        if self.current_dialog.do_animate_disappear and self.current_dialog.timer >= self.current_dialog.animation_length:
            self.current_dialog.closed = True
            self.current_dialog = None 

            if self.dialog_stack:
                self.current_dialog = self.dialog_stack.pop()
                self.current_dialog.do_animate_appear = True
                self.current_dialog.do_animate_disappear = False
                self.current_dialog.timer = 0
                self.in_dialog = True
            else:
                self.in_dialog = False
                self.wait_for_dialog_close = False
                
                if self.current_menu:
                    self.current_menu.reset_state()
    
    def animate_diff(self, current_menu, next_menu):
        """
        Animate the differences in anchored elements between the current and next menu
        """
        animate_back_button = False
        
        if 'back_button' in current_menu.main_body.definition and 'back_button' not in next_menu.main_body.definition:
            animate_back_button = True
        
        elif 'back_button' not in current_menu.main_body.definition and 'back_button' in next_menu.main_body.definition:
            animate_back_button = True
            
        elif 'back_button' not in current_menu.main_body.definition and 'back_button' not in next_menu.main_body.definition:
            animate_back_button = False
            
        elif current_menu.main_body.definition['back_button']['main_text']['display_text'] != next_menu.main_body.definition['back_button']['main_text']['display_text']:
            animate_back_button = True
            
        animate_footer_widget = False
        
        if 'footer_widgets' in current_menu.definition and 'footer_widgets' not in next_menu.definition:
            animate_footer_widget = True
        
        elif 'footer_widgets' not in current_menu.definition and 'footer_widgets' in next_menu.definition:
            animate_footer_widget = True
        
        elif 'footer_widgets' not in current_menu.definition and 'footer_widgets' not in next_menu.definition:
            animate_footer_widget = False
            
        elif len(current_menu.footer_widgets) != len(next_menu.footer_widgets):
            animate_footer_widget = True
        
        return animate_back_button, animate_footer_widget

    def handle_menu_transitions(self):
        """
        Handle the menu transitions
        """
        if self.next_menu is None:
            return
        
        if self.current_menu.doing_transition_animation:
            return
        
        if self.current_dialog is not None:
            return
        
        self.previous_menu = self.current_menu
        self.current_menu = self.next_menu
        
        animate_back_button, animate_footer_widget = self.animate_diff(self.previous_menu, self.current_menu)
        self.current_menu.do_menu_enter_transition_animation(animate_back_button, animate_footer_widget)
        self.next_menu = None
        
    def switch_menus(self, next_menu):
        """
        Switch to the next menu
        
        args:
            next_menu (Menu): The menu to switch to
        """
        self.next_menu = next_menu
        
        animate_back_button, animate_footer_widget = self.animate_diff(self.current_menu, next_menu)
        self.current_menu.do_menu_leave_transition_animation(animate_back_button, animate_footer_widget)
        
        if self.previous_menu is not None:
            self.previous_menu.reset_state()
            self.previous_menu = None
        
    def go_to_home(self):
        """
        Go to the home menu
        """
        self.switch_menus(self.home_menu)
    
    # home menu
    
    def go_to_multi(self):
        """
        Go to the multiplayer menu
        """
        self.switch_menus(self.multi_menu)
    
    def go_to_solo(self):
        """
        Go to the solo menu
        """ 
        self.switch_menus(self.solo_menu)
    
    def go_to_records(self): 
        """
        Go to the records menu
        """
        self.switch_menus(self.records_menu)
    
    def go_to_config(self):
        """
        Go to the config menu
        """
        self.switch_menus(self.config_menu)
    
    def go_to_about(self):
        """
        Go to the about menu
        """
        self.switch_menus(self.about_menu)
    
    def go_to_github(self):
        """
        Open the github page
        """
        self.current_menu.reset_state()
        webbrowser.open('https://github.com/Ma1achy/TETR.PY')
    
    # solo menu
    
    def go_to_40_lines(self):
        """
        Go to the 40 lines menu
        """
        self.switch_menus(self.forty_lines_menu)
    
    def go_to_blitz(self):
        """
        Go to the blitz menu
        """
        self.switch_menus(self.blitz_menu)
    
    def go_to_zen(self):
        """
        Go to the zen menu
        """
        self.switch_menus(self.zen_menu)
    
    def go_to_custom(self):
        """
        Go to the custom menu
        """
        self.switch_menus(self.custom_solo_menu)
    
    # config
    
    def go_to_account_settings(self):
        """
        Go to the account settings menu
        """
        self.switch_menus(self.account_menu)
    
    def export_settings(self):
        """
        Export the user settings
        """
        self.ConfigManager.export_user_settings(self.AccountManager.user)
    
    # error dialog 
    
    def handle_exceptions(self):
        """
        Handle exceptions
        """
        if self.Debug.ERROR is not None:
            self.__create_error_message_dialog()

        if self.ErrorDialog is not None:
            self.open_dialog(self.ErrorDialog)
        
    def __create_error_message_dialog(self): 
        """
        Create the error message dialog
        """
        if self.Debug.ERROR is None:
            return
        
        info, error, trace = self.Debug.ERROR
        self.Debug.ERROR = None
        self.ErrorDialog = DialogBox(self.Timing, self.window, self.Mouse, self.RenderStruct, title = 'UH OH . . .', message = f"TETR.PY has encountered a problem!\n [colour=#FF0000]{error}[/colour]\n \n [colour=#BBBBBB]{trace}[/colour]\nPlease report this problem at: \n https://github.com/Ma1achy/TETR.PY/issues", buttons = ['DISMISS', 'COPY'], funcs = [self.close_error_dialog, lambda: self.copy_to_clipboard(info)], click_off_dissmiss = False, width = 700)
    
    def close_error_dialog(self):
        """
        Close the error dialog
        """
        self.close_dialog()
        self.ErrorDialog = None
        self.switch_menus(self.home_menu)

    def update_darken_overlay_alpha(self):
        """
        Update the darken overlay alpha
        """
        if self.in_dialog and self.current_dialog is not self.LoginDialog:
            self.darken_overlay_layer_alpha =  min(self.current_dialog.alpha, 200)
        else:
            self.darken_overlay_layer_alpha = 0
    
    def render_copied_text(self):
        """
        Render the text to be used in the copy to clipboard animation
        """
        self.copied_text_surface_width, self.copied_text_surface_height = 900, 200
        self.copied_text_surface = pygame.surface.Surface((self.copied_text_surface_width, self.copied_text_surface_height), pygame.HWSURFACE|pygame.SRCALPHA)
        self.copied_text_surface_rect = pygame.Rect((self.RenderStruct.WINDOW_WIDTH - self.copied_text_surface_width)//2, (self.RenderStruct.WINDOW_HEIGHT - self.copied_text_surface_height)//2, self.copied_text_surface_width, self.copied_text_surface_height)
        
        self.copied_text = Font('d_din_bold', 90, None)
        self.copied_text.draw(self.copied_text_surface, 'COPIED TO CLIPBOARD!', '#FF7B10', 'center', 0, 5)
        self.copied_text.draw(self.copied_text_surface, 'COPIED TO CLIPBOARD!', '#FFD800', 'center', 0, 0)