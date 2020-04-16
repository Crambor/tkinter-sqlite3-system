"""
These imports are necessary for the modules within the SQL folder to be accessible by the main GUI.
Whenever 'SQL' is imported in a higher level directory, this script is run to relatively import
all the modules from the 'SQL' directory and make them usable to modules in higher level directories.
"""
from . import main

from . import users
from . import employees
from . import payments
from . import tenants
from . import apartments
from . import flats