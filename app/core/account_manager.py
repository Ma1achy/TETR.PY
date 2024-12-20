import configparser
import ast

class AccountManager():
    def __init__(self):
        
        self.parser = configparser.ConfigParser()
        self.accounts = ast.literal_eval(self.parser.get('USERS', 'ACCOUNTS', fallback = '[]'))
        self.user = None
        self.read_saved_login()
        
    def read_saved_login(self):
        self.parser.read('app\core\config\login.cfg')
        user = self.parser['LOGIN']['USER']
        
        if user == "":
            self.user = None
            
        if user in self.accounts:
            self.user = user
        else: 
            self.user = None
                 
    def save_login(self, user):
        self.parser.read('app/core/config/login.cfg')
        self.parser['LOGIN']['USER'] = "" if user is None else str(user)
        
        if user is not None and user not in self.accounts:
            self.accounts.append(user)
            self.parser['USERS']['ACCOUNTS'] = str(self.accounts)
        
        with open('app/core/config/login.cfg', 'w') as configfile:
            self.parser.write(configfile)