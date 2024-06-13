# This file is part of KanvasBuddy.

# KanvasBuddy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# KanvasBuddy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with KanvasBuddy. If not, see <https://www.gnu.org/licenses/>.

from configparser import ConfigParser
from os import path
import json

class KBConfigManager():
    _fileDir = path.dirname(path.realpath(__file__)) + '/'
    _propertiesFile = 'properties.json'
    _configFile = 'config.ini'

    def __init__(self):
        pass

    def loadProperties(self, section=''):
        data = None
        with open(self._fileDir + self._propertiesFile) as jsonFile:
            data = json.load(jsonFile)
            if section:
                data = data[section]

        return data

    def loadConfig(self, section=''):
        cfg = ConfigParser()
        cfg.optionxform = str # Prevents ConfigParser from turning all entrys lowercase 
        cfg.read(self._fileDir + self._configFile)

        if section:
            cfg = cfg[section]

        return cfg
