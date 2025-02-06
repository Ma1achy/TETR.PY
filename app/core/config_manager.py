import configparser
import ast
import os
import sys
import tkinter as tk
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtGui import QIcon
from tkinter import filedialog
import threading
from enum import Enum
from enum import auto

from app.input.keyboard.menu_kb_input_handler import UIAction
from instance.handling.handling import Action
from render.render import StructRender

if sys.platform == "darwin":
    import os
    os.environ["TK_SILENCE_DEPRECATION"] = "1"
    
class ConfigManager():
    def __init__(self, WorkerManager):
        """
        The configuration manager
        
        args:
            WorkerManager (WorkerManager): The WorkerManager instance
        """
        self.WorkerManager = WorkerManager
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
        
        self.user = None
        self.in_export_window = False
        self.lock = threading.Lock()
        
        self.missing_sections = []
        self.loaded_sections = []
        
        self.load_default_settings()
        self.load_defualt_handling()
        self.load_default_keybindings()
        
        self.RenderStruct = StructRender()
        self.config_is_malformed = False
        self.error_loading_config = False
        
    def load_defualt_handling(self):
        """
        Load the default handling settings
        """
        self.parser.read('app/core/config/default_handling.cfg')
        self.default_handling_settings = {key: self.convert_value(value) for key, value in self.parser['HANDLING_SETTINGS'].items()}

        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
        
    def load_default_keybindings(self):
        """
        Load the default keybindings
        """
        self.parser.read('app/core/config/default_keybindings.cfg')
        self.guideline_keybindings = {key: self.convert_value(value) for key, value in self.parser['GUIDELINE_KEYBINDINGS'].items()}
        self.wasd_keybindings = {key: self.convert_value(value) for key, value in self.parser['WASD_KEYBINDINGS'].items()}
        
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
        
    def load_default_settings(self):
        """
        Load the default settings
        """
        self.parser.read('app/core/config/default.cfg')
        
        self.default_controls_settings      =   self.load_section('CONTROLS_SETTINGS')
        self.default_custom_keybindings     =   self.load_section('CUSTOM_KEYBINDINGS')
        self.default_handling_settings      =   self.load_section('HANDLING_SETTINGS')
        self.default_audio_settings         =   self.load_section('AUDIO_SETTINGS')
        self.default_gameplay_settings      =   self.load_section('GAMEPLAY_SETTINGS')
        self.default_video_settings         =   self.load_section('VIDEO_SETTINGS')
        self.default_customisation_settings =   self.load_section('CUSTOMISATION_SETTINGS')
        
        self.default_forty_lines_settings   =   self.load_section('40L_SETTINGS')
        self.default_blitz_settings         =   self.load_section('BLITZ_SETTINGS')
        
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
    
    def load_section(self, section, default = None):
        if section not in self.parser.sections():
            if default is not None:
                self.missing_sections.append(section)
                self.config_is_malformed = True
                return default
        
        self.loaded_sections.append(section)
        return {key: self.convert_value(value) for key, value in self.parser[section].items()}
          
    def load_user_settings(self, user):
        """
        Load the user settings
        """
        try:
            self.user = user
            cfg = f'@{user}.cfg'
            path = os.path.join('app/core/config', cfg)
            
            if not os.path.exists(path):
                self.create_user_settings(user)

            self.parser.read(path)
            self.load_settings()
        except Exception as e:
            self.parser.read('app/core/config/default.cfg')
            self.load_settings()
            os.remove(path)
            self.create_user_settings(user)
            self.error_loading_config = True
        
    def create_user_settings(self, user):
        """
        Create the user settings
        
        args:
            user (str): the user to create the settings for
        """
        if user == '' or user is None:
            return
        
        cfg = f'@{user}.cfg'
        path = os.path.join('app/core/config', cfg)
        
        with open('app/core/config/default.cfg', 'r') as f:
            with open(path, 'w') as new:
                new.write(f.read())
    
    def reset_handling_settings(self):
        """
        Reset the handling settings
        """
        self.handling_settings = self.default_handling_settings.copy()
        
        for key, value in self.handling_settings.items():
            self.save_setting_change('HANDLING_SETTINGS', key, value)
        
    def load_settings(self):
        """
        Load the settings
        """ 
        self.config_is_malformed = False
        
        self.controls_settings      =   self.load_section('CONTROLS_SETTINGS', self.default_controls_settings)
        self.custom_keybindings     =   self.load_section('CUSTOM_KEYBINDINGS', self.default_custom_keybindings)
        self.handling_settings      =   self.load_section('HANDLING_SETTINGS', self.default_handling_settings)
        self.audio_settings         =   self.load_section('AUDIO_SETTINGS', self.default_audio_settings)
        self.gameplay_settings      =   self.load_section('GAMEPLAY_SETTINGS', self.default_gameplay_settings)
        self.video_settings         =   self.load_section('VIDEO_SETTINGS', self.default_video_settings)
        self.customisation_settings =   self.load_section('CUSTOMISATION_SETTINGS', self.default_customisation_settings)
        
        self.forty_lines_settings   =   self.load_section('40L_SETTINGS', self.default_forty_lines_settings)
        self.blitz_settings         =   self.load_section('BLITZ_SETTINGS', self.default_blitz_settings)
        
        self.validate()
        self.set_keybindings()

        self.update_video_settings()
        self.RenderStruct.MUST_RESTART_TO_APPLY_CHANGES = True
        
    def validate(self):
        """
        Validate the loaded settings and repair the configuration file if necessary
        """
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
        
        self.validate_section(self.controls_settings, self.default_controls_settings, 'CONTROLS_SETTINGS')
        self.validate_section(self.custom_keybindings, self.default_custom_keybindings, 'CUSTOM_KEYBINDINGS')
        self.validate_section(self.handling_settings, self.default_handling_settings, 'HANDLING_SETTINGS')
        self.validate_section(self.audio_settings, self.default_audio_settings, 'AUDIO_SETTINGS')
        self.validate_section(self.gameplay_settings, self.default_gameplay_settings, 'GAMEPLAY_SETTINGS')
        self.validate_section(self.video_settings, self.default_video_settings, 'VIDEO_SETTINGS')
        self.validate_section(self.customisation_settings, self.default_customisation_settings, 'CUSTOMISATION_SETTINGS')
        
        self.validate_section(self.forty_lines_settings, self.default_forty_lines_settings, '40L_SETTINGS')
        self.validate_section(self.blitz_settings, self.default_blitz_settings, 'BLITZ_SETTINGS')
        
        self.save_config()
        self.validate_settings()
        
    def validate_section(self, loaded, default, section): 
        file = f'@{self.user}.cfg'
        path = os.path.join('app/core/config', file)
        
        with open(path, 'w') as configfile:
            self.parser.write(configfile)

        if section not in self.parser.sections():
            self.parser.add_section(section)

        if section in self.loaded_sections:
            for key, value in loaded.items():
                self.parser[section][key] = str(value)
        
        if section in self.missing_sections:
            for key, value in default.items():
                self.parser[section][key] = str(value)
           
    def validate_settings(self):
      
        self.validate_setting(self.controls_settings, self.default_controls_settings, 'CONTROLS_SETTINGS')
        self.validate_setting(self.custom_keybindings, self.default_custom_keybindings, 'CUSTOM_KEYBINDINGS')
        self.validate_setting(self.handling_settings, self.default_handling_settings, 'HANDLING_SETTINGS')
        self.validate_setting(self.audio_settings, self.default_audio_settings, 'AUDIO_SETTINGS')
        self.validate_setting(self.gameplay_settings, self.default_gameplay_settings, 'GAMEPLAY_SETTINGS')
        self.validate_setting(self.video_settings, self.default_video_settings, 'VIDEO_SETTINGS')
        self.validate_setting(self.customisation_settings, self.default_customisation_settings, 'CUSTOMISATION_SETTINGS')
        
        self.validate_setting(self.forty_lines_settings, self.default_forty_lines_settings, '40L_SETTINGS')
        self.validate_setting(self.blitz_settings, self.default_blitz_settings, 'BLITZ_SETTINGS')
                
    def validate_setting(self, loaded, default, section):
        for key, value in default.items():
            if key not in loaded:
                self.edit_setting(section, key, value)
                self.config_is_malformed = True
                    
    def set_keybindings(self):
        if self.controls_settings['SELECTED'] == 'GUIDELINE_KEYBINDINGS':
            keybindings = self.guideline_keybindings
        elif self.controls_settings['SELECTED'] == 'WASD_KEYBINDINGS':
            keybindings = self.wasd_keybindings
        else:
            keybindings = self.custom_keybindings
            
        self.menu_keybindings = {action: keybindings[action.name] for action in UIAction if action.name in keybindings}
        self.menu_keybindings[UIAction.MENU_DEBUG] = ['f3']
        self.menu_keybindings[UIAction.WINDOW_FULLSCREEN] = ['f11']
        self.menu_keybindings[UIAction.RESTART_APP] = ['f5']
        
        self.game_keybindings = {action: keybindings[action.name] for action in Action if action.name in keybindings}
               
    def get_setting_value(self, section, key):
        """
        Get the value of a setting
        
        args:
            section (str): the section to get the setting from
            key (str): the key to get the setting from
        """
        match section:
            case 'CONTROLS_SETTINGS':
                return self.controls_settings[key]
            case 'CUSTOM_KEYBINDINGS':
                return self.custom_keybindings[key]
            case 'HANDLING_SETTINGS':
                return self.handling_settings[key]
            case 'AUDIO_SETTINGS':
                return self.audio_settings[key]
            case 'GAMEPLAY_SETTINGS':
                return self.gameplay_settings[key]
            case 'VIDEO_SETTINGS':
                return self.video_settings[key]
            case 'CUSTOMISATION_SETTINGS':
                return self.customisation_settings[key]
            case '40L_SETTINGS':
                return self.forty_lines_settings[key]
            case 'BLITZ_SETTINGS':
                return self.blitz_settings[key]
            case _:
                return
        
    def edit_setting(self, section, key, value):
        """
        Edit the setting
        
        args:
            section (str): the section to edit the setting in
            key (str): the key to edit the setting in
            value (str): the value to edit
        """
        match section:
            case 'CONTROLS_SETTINGS':
                self.controls_settings[key] = value
            case 'CUSTOM_KEYBINDINGS':
                self.custom_keybindings[key] = value
            case 'HANDLING_SETTINGS':
                self.handling_settings[key] = value
            case 'AUDIO_SETTINGS':
                self.audio_settings[key] = value
            case 'GAMEPLAY_SETTINGS':
                self.gameplay_settings[key] = value
            case 'VIDEO_SETTINGS':
                self.video_settings[key] = value
                self.update_video_settings()
            case 'CUSTOMISATION_SETTINGS':
                self.customisation_settings[key] = value
            case '40L_SETTINGS':
                self.forty_lines_settings[key] = value
            case 'BLITZ_SETTINGS':
                self.blitz_settings[key] = value
            case _:
                return
        
        self.save_setting_change(section, key, value)
        
    def save_setting_change(self, section, key, value):
        """
        Save the setting change
        
        args:
            section (str): the section to save the setting to
            key (str): the key to save the setting to
            value (str): the value to save
        """
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser[section][key] = str(value)
        self.save_config()
    
    def save_config(self):
        if sys.platform == 'win32':
            self.WorkerManager.add_task(self.write_to_file)
        else:
            self.write_to_file()
            
    def write_to_file(self):
        """
        Save the configuration
        """
        with self.lock:
            cfg = f'@{self.user}.cfg'
            path = os.path.join('app/core/config', cfg)
            
            with open(path, 'w') as configfile:
                self.parser.write(configfile)
                
    def convert_value(self, value):
        """
        Convert the value to the correct type
        
        args:
            value (str): the value to convert
        """
        if value in ['True', 'False']:
            return value == 'True'
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def export_user_settings(self, user):
        """
        Export the user settings
        
        args:
            user (str): the user to export the settings for
        """        
        if self.in_export_window:
            return
        
        self.user = user
        
        if sys.platform == 'win32':
            self.in_export_window = True
            self.WorkerManager.add_task(self.export_file_windows)
        else:
            self.export_file_unix()
        
    def export_file_windows(self):
        """
        Open a file dialog to export the settings to a configuration file
        """
        cfg = f'@{self.user}.cfg'

        root = tk.Tk()
        root.withdraw()
            
        if sys.platform == 'win32':
            root.iconbitmap('resources/icon.ico')
        try:
            save_path = filedialog.asksaveasfilename(defaultextension = ".cfg", initialfile = cfg, title = "TETR.PY: Export Configuration File", filetypes = [("Config Files", "*.cfg"), ("All Files", "*.*")])
           
            if save_path:
                with open(save_path, 'w') as configfile:
                    self.parser.write(configfile)
                    
        except Exception as e:
            print(f"\033[91mError exporting configuration file: {e}\033[0m")
        finally:
            root.destroy()
                
        self.in_export_window = False
    
    def export_file_unix(self):
        """
        Open a file dialog to export the settings to a configuration file
        Have to use PyQt5 here because tkinter was giving me issues on macOS ??
        """
        cfg = f'@{self.user}.cfg'
        
        app = QApplication([])
        app.setWindowIcon(QIcon('resources/icon.png'))
        
        try:
            default_directory = os.path.expanduser("~/Desktop")
            default_file_path = os.path.join(default_directory, cfg)
            save_path, _ = QFileDialog.getSaveFileName(None, "TETR.PY: Export Configuration File", default_file_path, "Config Files (*.cfg);;All Files (*)")
            
            if save_path:
                with open(save_path, 'w') as configfile:
                    self.parser.write(configfile)
                    
        except Exception as e:
            print(f"\033[91mError exporting configuration file: {e}\033[0m")
        finally:
            app.quit()
            
        self.in_export_window = False
    
    def toggle_fullscreen(self):
        """
        Toggle fullscreen
        """
        bool = not self.video_settings['FULLSCREEN']
        self.edit_setting('VIDEO_SETTINGS', 'FULLSCREEN', bool)
        
    def update_video_settings(self):
        self.render_scale_restart = False
        self.update_target_fps()
        self.update_fullscreen()
        self.update_render_scale_mode()
        self.update_render_scale_factor()
       
    def update_target_fps(self):
        if self.RenderStruct.TARGET_FPS == self.video_settings['TARGET_FPS']:
            return
        
        self.RenderStruct.TARGET_FPS = self.video_settings['TARGET_FPS']
        
    def update_fullscreen(self):
        if self.RenderStruct.FULLSCREEN == self.video_settings['FULLSCREEN']:
            return
        
        self.RenderStruct.FULLSCREEN = self.video_settings['FULLSCREEN']
            
    def update_render_scale_factor(self):
        if self.RenderStruct.RENDER_SCALE == self.video_settings['RENDER_SCALE'] / 100:
            return  
        
        if self.RenderStruct.MUST_RESTART_TO_APPLY_CHANGES:
            return
        
        self.RenderStruct.RENDER_SCALE = self.video_settings['RENDER_SCALE'] / 100
            
    def update_render_scale_mode(self):
        if self.RenderStruct.RENDER_SCALE_MODE == self.video_settings['RENDER_SCALE_MODE']:
            return
        
        if self.RenderStruct.MUST_RESTART_TO_APPLY_CHANGES:
            return
            
        if self.video_settings['RENDER_SCALE_MODE'] == "OFF":
            self.video_settings['RENDER_SCALE'] = 100
            
        self.RenderStruct.RENDER_SCALE_MODE = self.video_settings['RENDER_SCALE_MODE']

class ControlsSettings():
    SELECTED: str = "GUIDELINE_KEYBINDINGS"
     
class HandlingSettings():
    ARR: int = 33
    DAS: int = 167
    DCD: int = 17
    SDF: int = 6
    
    PREVENT_ACCIDENTAL_HARDDROPS: bool = True
    DAS_CANCEL: bool = False
    PREFER_SOFTDROP_OVER_MOVEMENT: bool = True
    PRIORITISE_MOST_RECENT_DIRECTION: bool = True
    
class AudioSettings():
    MUSIC_VOLUME: float = 1.0
    SFX_VOLUME: float = 1.0
    STEREO_BALANCE: float = 0.5
    
    SCROLL_TO_CHANGE_VOLUME: bool  = True
    MUTE_WHEN_HIDDEN: bool  = True
    HEAR_NEXT_PIECE: bool = True
    HEAR_OTHER_PLAYERS: bool = True
    HEAR_ATTACKS: bool = True
    DO_NOT_RESET_MUSIC_ON_RETRY: bool = True
    DISABLE_ALL_SOUND: bool = False
    
class GameplaySettings():
    ACTION_TEXT_SELECTION: str = "ALL"
    
    BOARD_BOUNCINESS: float = 1.0
    DAMAGE_SHAKINESS: float = 1.0
    GRID_VISIBILITY: float = 1.0
    BOARD_VISIBILITY: float = 8.5
    SHADOW_VISIBILITY: float = 1.0
    BOARD_ZOOM: float  = 1.0
    
    SHOW_DUELS_SIDE_BY_SIDE: bool = True
    SPIN_BOARD_WHEN_SPIN: bool = True
    ALERT_WHEN_KO: bool = True
    WARN_WHEN_IN_DANGER: bool = True
    COLOURED_SHADOW: bool = True
    GRAY_OUT_LOCKED_HOLD: bool = True
    
class VideoSettings():
    GRAPHICS_MODE: str = "HIGH"

    TARGET_FPS: int = "INF"
    PARTICLE_COUNT: float = 1.0
    BACKGROUND_VISIBILITY: float = 7.0

    RENDER_SCALE_MODE: str = "OFF"
    RENDER_SCALE: float = 1.0

    FULLSCREEN: bool = False
    ALWAYS_SIMPLIFY_OTHER_BOARDS: bool = False
    NO_BACKGROUND_IN_MENUS: bool = False
    KEEP_REPLAY_TOOLS_OPEN: bool = False
    WARN_WHEN_NOT_FOCUSED: bool = True
        
class CustomisationSettings():
    USE_CUSTOM_BACKGROUND: bool= False
    CUSTOM_BACKGROUND_PATHS: list = []
    BLOCK_SKIN: str = "DEFAULT"
    CUSTOM_BLOCK_SKIN_PATH: str = None

class FortyLinesSettings():
    PRO_MODE: bool = False
    ALERT_ON_FINESSE_FAULT: bool = False
    RETRY_ON_FINESSE_FAULT: bool = False
    STRIDE_MODE: bool = False

    LEFT_COUNTER_SLOT_1: bool = None
    LEFT_COUNTER_SLOT_2: bool = None
    LEFT_COUNTER_SLOT_3: bool = None
    LEFT_COUNTER_SLOT_4: bool = None
    RIGHT_COUNTER_SLOT: bool = None
    
class BlitzSettings():
    PRO_MODE: bool = False
    ALERT_ON_FINESSE_FAULT: bool = False
    RETRY_ON_FINESSE_FAULT: bool = False
    STRIDE_MODE: bool = False

    LEFT_COUNTER_SLOT_1: bool = None
    LEFT_COUNTER_SLOT_2: bool = None
    LEFT_COUNTER_SLOT_3: bool = None
    LEFT_COUNTER_SLOT_4: bool = None
    RIGHT_COUNTER_SLOT: bool = None

# FIXME: need to change how config file is loaded, as currently if there is no user logged in it crashes
# need to probably change the logic/simplify it and this seems bad? although the error handling/validation and malform fixing is good.
# need to change it so the setting changes change the value of the setting class I've made so the change happens globally