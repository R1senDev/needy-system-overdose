'''
PLatform INDependent Functions
'''

# Shared stuff
from platform import system
from getpass  import getuser
from classes  import Point
from ctypes   import byref
from re       import search


is_windows = system() == 'Windows'


match system():

    ###############
    ##  WINDOWS  ##
    ###############

    case 'Windows':

        from ctypes import windll # type: ignore

        APP_DATA_ROOT = f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\'
        SETTINGS_PATH = APP_DATA_ROOT + 'settings.json'

        kernel32 = windll.kernel32

        def get_absolute_cursor_position() -> list[int]:
            point = Point()
            windll.user32.GetCursorPos(byref(point))
            return [point.x, point.y]

        def get_uptime() -> float:
            # Using float to unify return type
            return float(kernel32.GetTickCount64())


    #############
    ##  LINUX  ##
    #############

    case 'Linux':

        from Xlib.display import Display # type: ignore

        APP_DATA_ROOT = f'/home/{getuser()}/.local/share/needysys/'
        SETTINGS_PATH = APP_DATA_ROOT + 'settings.json'

        def get_absolute_cursor_position() -> list[int]:
            display = Display()
            root = display.screen().root
            pointer = root.query_pointer()
            x, y = pointer.root_x, pointer.root_y
            return [x, y]

        def get_uptime() -> float:
            with open('/proc/uptime', 'r') as file:
                data = file.read()
            result = search(r'\d+\.\d+', data)
            if result is None:
                return -1.0
            return float(result.group(0))


    ###############################
    ##  TRASH (DARWIN INCLUDED)  ##
    ###############################

    case _:

        raise OSError(f'Platform "{system()}" is not supported by NSO.')


if __name__ == '__main__':
    from time import sleep
    while True:
        print(*get_absolute_cursor_position())
        sleep(1)