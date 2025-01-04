import configparser
import ast
import os
import sys
import tkinter as tk
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtGui import QIcon
from tkinter import filedialog
import threading

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
        
        self.user = None
        self.in_export_window = False
        
        self.load_defualt_handling()
        self.load_default_keybindings()
        
    def load_defualt_handling(self):
        """
        Load the default handling settings
        """
        self.parser.read('app/core/config/default_handling.cfg')
        self.default_handling_settings = {key: self.convert_value(value) for key, value in self.parser['HANDLING_SETTINGS'].items()}
    
    def load_default_keybindings(self):
        """
        Load the default keybindings
        """
        self.parser.read('app/core/config/default_keybindings.cfg')
        self.guidline_keybindings = {key: self.convert_value(value) for key, value in self.parser['GUIDLINE_KEYBINDINGS'].items()}
        self.wasd_keybindings = {key: self.convert_value(value) for key, value in self.parser['WASD_KEYBINDINGS'].items()}
            
    def load_default_settings(self):
        """
        Load the default settings
        """
        self.parser.read('app/core/config/default.cfg')
        self.load_settings()
    
    def load_user_settings(self, user):
        """
        Load the user settings
        """
        cfg = f'@{user}.cfg'
        path = os.path.join('app/core/config', cfg)
        
        if not os.path.exists(path):
            self.create_user_settings(user)

        self.parser.read(path)
        self.load_settings()
        
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
    
    def load_settings(self):
        """
        Load the settings
        """
        self.controls_settings      =   {key: self.convert_value(value) for key, value in self.parser['CONTROLS_SETTINGS'].items()}
        self.custom_keybindings     =   {key: self.convert_value(value) for key, value in self.parser['CUSTOM_KEYBINDINGS'].items()}
        self.handling_settings      =   {key: self.convert_value(value) for key, value in self.parser['HANDLING_SETTINGS'].items()}
        self.audio_settings         =   {key: self.convert_value(value) for key, value in self.parser['AUDIO_SETTINGS'].items()}
        self.gameplay_settings      =   {key: self.convert_value(value) for key, value in self.parser['GAMEPLAY_SETTINGS'].items()}
        self.video_settings         =   {key: self.convert_value(value) for key, value in self.parser['VIDEO_SETTINGS'].items()}
        
        print(self.controls_settings)
        print(self.custom_keybindings)
        print(self.handling_settings)
        print(self.audio_settings)
        print(self.gameplay_settings)
        print(self.video_settings)
    
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

        print(f"Current thread: {threading.current_thread().name}")
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
        
        print(f"Current thread: {threading.current_thread().name}")
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