import sys
sys.path.insert(0, '/var/www/peoplesparql')
from peoplesparql import app as application
activate_this = '/home/geekscruff/Envs/flenv/bin/activate_this.py'
execfile(activate_this, dict(file=activate_this))