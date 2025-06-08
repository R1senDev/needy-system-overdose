from platform import system
from re import match

from .utils import UtilitaryClass

import os


class HWSensor:

    def __init__(self, name: str, values: dict[str, int]) -> None:

        self.name = name.strip('\n')
        self.values = {key: values[key] for key in sorted(values)}

    @property
    def dict(self) -> dict[str, str | dict[str, int]]:
        return {'name': self.name, 'values': self.values}
    

class HWMonitor(UtilitaryClass):

    HWMON_ROOT = '/sys/class/hwmon/'
    weirdo = False
    
    @classmethod
    def _linux_get_metrics(cls, include_patterns: list[str] | None = None) -> list[HWSensor]:

        if not os.path.isdir(cls.HWMON_ROOT):
            return []
        
        sensors: list[HWSensor] = []
        
        for hwmon_name in os.listdir(cls.HWMON_ROOT):

            hwmon = os.path.join(cls.HWMON_ROOT, hwmon_name)
            data: dict[str, int] = {}

            with open(os.path.join(hwmon, 'name'), 'r') as file:
                name = file.read()

            for metric_name in os.listdir(hwmon):
                metric = os.path.join(hwmon, metric_name)

                if include_patterns is None:
                    match_flag = True
                else:
                    match_flag = any([match(pattern, metric_name) is not None for pattern in include_patterns]) and metric_name.endswith('input')

                if os.path.isfile(metric) and match_flag:
                    with open(metric, 'r') as file:
                        try:
                            data[metric_name.split('_', 1)[0]] = int(file.read())
                        except ValueError:
                            continue
                
            sensors.append(HWSensor(name, data))

        return sensors
    
    @classmethod
    def _windows_get_metrics(cls, include_patterns: list[str] | None = None) -> list[HWSensor]:
        if not cls.weirdo:
            print('[WARN] Fetching hardware montors\' data is not supported on Windows yet. Planned in NSO>=3.0.0.')
            cls.weirdo = True
        return []
    
    @classmethod
    def _unknown_system_get_metrics(cls) -> list[HWSensor]:
        if not cls.weirdo:
            print(f'[WARN] Fetching hardware montors\' data is not supported on this system ("{system()}"). Planned in NSO>=3.0.0.')
            cls.weirdo = True
        return []
    
    @classmethod
    def get_metrics(cls, include_patterns: list[str] | None = None) -> list[HWSensor]:

        match system():

            case 'Windows': return cls._windows_get_metrics(include_patterns)
            case 'Linux':   return cls._linux_get_metrics(include_patterns)
            case _:         return cls._unknown_system_get_metrics()


if __name__ == '__main__':
    from json import dumps
    from time import sleep
    try:
        while True:
            os.system('clear || cls')
            print(dumps([metric.dict for metric in HWMonitor.get_metrics()], indent = 4))
            sleep(1)
    except KeyboardInterrupt:
        exit(0)