import configparser
import ast

class AccountManager():
    def __init__(self, ConfigManager):
        
        self.parser = configparser.ConfigParser()
        self.accounts = self.get_accounts()
        self.user = None
        self.read_saved_login()
        self.ConfigManager = ConfigManager
    
    def get_accounts(self):
        """
        Get the accounts from the config file
        """
        self.parser.read('config/login.cfg')
        accounts = self.parser['USERS']['ACCOUNTS']
        
        if accounts == "[]":
            return []
        
        return ast.literal_eval(accounts)
    
    def read_saved_login(self):
        """
        Read the saved login from the config file
        """
        self.parser.read('config/login.cfg')
        user = self.parser['LOGIN']['USER']
        
        if user == "":
            self.user = None
            return
            
        if self.user_exists(user):
            self.user = user
            return
  
        self.user = None
        
    def login(self, user):
        """
        Log in as a user
        
        args:
            user (str): the user to log in as
        """
        if not self.user_exists(user):
            self.create_user(user)
        
        self.save_login(user)
        self.user = user
        self.ConfigManager.load_user_settings(user)
               
    def save_login(self, user):
        """
        Save the login to the config file
        
        args:
            user (str): the user to save
        """
        if user is None:
            return
         
        with open('config/login.cfg', 'r') as configfile:
            self.parser.read_file(configfile)
 
        self.parser['LOGIN']['USER'] = user

        with open('config/login.cfg', 'w') as configfile:
            self.parser.write(configfile)
        
    def user_exists(self, user):
        """
        Check if a user exists
        
        args:
            user (str): the user to check
        """
        if user in self.accounts:
            return True
        else:
            return False
    
    def create_user(self, user):
        """
        Create a user
        
        args:
            user (str): the user to create
        """
        if self.user_exists(user):
            return
                
        self.accounts.append(user)
        self.parser['USERS']['ACCOUNTS'] = str(self.accounts)
        
        with open('config/login.cfg', 'w') as configfile:
            self.parser.write(configfile)
    
    def delete_user(self, user):
        """
        Delete a user
        
        args:
            user (str): the user to delete
        """
        if not self.user_exists(user):
            return
        
        self.accounts.remove(user)
        self.parser['USERS']['ACCOUNTS'] = str(self.accounts)
        
        with open('config/login.cfg', 'w') as configfile:
            self.parser.write(configfile)
    
    def logout(self):
        """
        Log out of the current user
        """
        self.save_login("")
        self.ConfigManager.load_default_settings()
        self.user = None