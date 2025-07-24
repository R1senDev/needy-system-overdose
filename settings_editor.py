from core.plindf import SETTINGS_PATH
from typing      import Any
from json        import load, dump


with open(SETTINGS_PATH, 'r') as file:
    settings: dict[str, Any] = load(file)


while True:
    key = input('\nEnter settings key to set ("APPLY" to commit changes, "EXIT" to revert): ')
    if key == 'APPLY':
        with open(SETTINGS_PATH, 'w') as file:
            dump(settings, file)
            key = 'EXIT'
    if key == 'EXIT':
        print('Bye!\n')
        break
    if key not in settings.keys():
        print(f'No such key: {key}. Try again.')
        continue
    value = input('Enter new value to set: ')
    key_type = type(settings[key])
    try:
        value = key_type(value)
    except ValueError:
        print(f'That\'s not how it works. Types mismatch: {key_type.__name__} expected. Try again.')
        continue
    settings[key] = value
    print(f'Okay! settings.{key} == {value} ({type(value).__name__})')