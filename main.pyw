# base imports
import os

# module imports
import GUI
import SQL

# Creates the directory for the database if it doesn't exist, and sets the path into that directory
cwd = os.getcwd() + "\\data"
if not os.path.isdir(cwd):
    os.mkdir(cwd)
os.chdir(cwd)

# Establishes the connection to the database and creates the tables if they do not already exist.
SQL.main.establish_connection('Prototype.db')
SQL.main.create_tables()

# Creates the application
GUI.Application()
