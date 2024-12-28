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
        self.parser.read('app\core\config\login.cfg')
        accounts = self.parser['USERS']['ACCOUNTS']
        
        if accounts == "[]":
            return []
        
        return ast.literal_eval(accounts)
    
    def read_saved_login(self):
        self.parser.read('app\core\config\login.cfg')
        user = self.parser['LOGIN']['USER']
        
        if user == "":
            self.user = None
            return
            
        if self.user_exists(user):
            self.user = user
            return
  
        self.user = None
        
    def login(self, user):
        if not self.user_exists(user):
            self.create_user(user)
        
        self.save_login(user)
        self.user = user
        print(f"Logged in as {user}")
        self.ConfigManager.load_user_settings(user)
               
    def save_login(self, user):
        if user is None:
            return
         
        with open('app/core/config/login.cfg', 'r') as configfile:
            self.parser.read_file(configfile)
 
        self.parser['LOGIN']['USER'] = user

        with open('app/core/config/login.cfg', 'w') as configfile:
            self.parser.write(configfile)
        
    def user_exists(self, user):
        if user in self.accounts:
            return True
        else:
            return False
    
    def create_user(self, user):
        if self.user_exists(user):
            return
                
        self.accounts.append(user)
        self.parser['USERS']['ACCOUNTS'] = str(self.accounts)
        
        with open('app/core/config/login.cfg', 'w') as configfile:
            self.parser.write(configfile)
    
    def delete_user(self, user):
        if not self.user_exists(user):
            return
        
        self.accounts.remove(user)
        self.parser['USERS']['ACCOUNTS'] = str(self.accounts)
        
        with open('app/core/config/login.cfg', 'w') as configfile:
            self.parser.write(configfile)
    
    def logout(self):
        self.save_login("")
        self.ConfigManager.load_default_settings()
        self.user = None