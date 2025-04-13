from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

login_manager = LoginManager()
bcrypt = Bcrypt()
mysql = MySQL()
