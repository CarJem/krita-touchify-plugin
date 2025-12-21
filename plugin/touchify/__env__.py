import os;

#-----------------#
# Enviornment Variables
BASE_DIR = os.path.dirname(os.path.realpath(__file__)) 
REGISTERED_ACTIONS_FILE = os.path.dirname(os.path.realpath(__file__)) + "/registered_actions.action"
RESOURCE_PACKS_DIRECTORY=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')
#-----------------#