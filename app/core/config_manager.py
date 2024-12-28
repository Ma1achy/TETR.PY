import configparser
import ast
import os
import tkinter as tk
from tkinter import filedialog
import threading
class ConfigManager():
    def __init__(self, WorkerManager):
        self.WorkerManager = WorkerManager
        self.parser = configparser.ConfigParser()
        
        self.user = None
        self.in_export_window = False
        
        self.load_defualt_handling()
        self.load_default_keybindings()
        
    def load_defualt_handling(self):
        self.parser.read('app/core/config/default_handling.cfg')
        self.default_handling_settings = {key: self.convert_value(value) for key, value in self.parser['HANDLING_SETTINGS'].items()}
    
    def load_default_keybindings(self):
        self.parser.read('app/core/config/default_keybindings.cfg')
        self.guidline_keybindings = {key: self.convert_value(value) for key, value in self.parser['GUIDLINE_KEYBINDINGS'].items()}
        self.wasd_keybindings = {key: self.convert_value(value) for key, value in self.parser['WASD_KEYBINDINGS'].items()}
            
    def load_default_settings(self):
        self.parser.read('app/core/config/default.cfg')
        self.load_settings()
    
    def load_user_settings(self, user):
        cfg = f'@{user}.cfg'
        path = os.path.join('app/core/config', cfg)
        
        if not os.path.exists(path):
            self.create_user_settings(user)

        self.parser.read(path)
        self.load_settings()
        
    def create_user_settings(self, user):
        if user == '' or user is None:
            return
        
        cfg = f'@{user}.cfg'
        path = os.path.join('app/core/config', cfg)
        
        with open('app/core/config/default.cfg', 'r') as f:
            with open(path, 'w') as new:
                new.write(f.read())
    
    def load_settings(self):
  
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
        if value in ['True', 'False']:
            return value == 'True'
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    def export_user_settings(self, user):
        self.user = user
    
        if not self.in_export_window:
            self.in_export_window = True
            self.WorkerManager.add_task(self.save_file)
                
    def save_file(self):
        cfg = f'@{self.user}.cfg'
        
        root = tk.Tk()
        root.withdraw()
        root.iconbitmap('resources/icon.ico')
        
        save_path = filedialog.asksaveasfilename(defaultextension = ".cfg", initialfile = cfg, title = "TETR.PY: Export Configuration File", filetypes = [("Config Files", "*.cfg"), ("All Files", "*.*")])
        
        if save_path:
            with open(save_path, 'w') as configfile:
                self.parser.write(configfile)
            
        self.in_export_window = False