"""
Author:
melektron
"""

import json as j
from typing import Any

class ConfigPermissionError (Exception):
    ...


class _confhive:
    def __init__(self, hivefile: str) -> None:
        self.__hivefile = hivefile

        # load the config hive file
        self.__hive: dict = j.load(hivefile)

        # get the hive name and permissions
        self.__hivename: str = self.__hive["hivename"]
        self.__wprot: bool = self.__hive["writeprotect"]

        # load all the values
        for key, value in self.__hive["keys"]:
            # load arguments
            setattr(self, key, value)

    def setkey(self, config_key: str, value: Any) -> None:
        if self.__wprot:
            raise ConfigPermissionError(f"Config hive {self.__hivename} is write protected")
        
        self.__hive["keys"][config_key] = value
        j.dump(self.__hive, self.__hivefile)
    




