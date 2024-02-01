from threading import Thread
from getpass   import getuser
from psutil    import cpu_percent, virtual_memory, disk_usage
from string    import ascii_uppercase
from typing    import Callable
from ctypes    import windll
from json      import load, dump
from time      import sleep
from os        import makedirs
import pyglet


settings_shown = False
forced_c_selection = False

bg_offset = 0


try:
    makedirs(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\')
    settings = {
        'enable_animations': True,
        'disk_index': 2,
        'shorter_update_interval': False,
        'enable_bg_animation': False,
        'blocks_transparency': 204
    }
    with open(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\settings.json', 'w') as file:
        dump(settings, file)
except OSError:
    with open(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\settings.json', 'r') as file:
        settings = load(file)


def szfill(num: int | float | str, before_dot: int = 2) -> str:
    num = str(num)
    while len(num.split('.')[0]) < before_dot: num = f'0{num}'
    return num


window = pyglet.window.Window(
    width     = 850,
    height    = 600,
    resizable = False,
    caption = 'NeedySystemOverdose'
)


bg_batch             = pyglet.graphics.Batch()
fg_batch             = pyglet.graphics.Batch()
character_batch      = pyglet.graphics.Batch()
anim_character_batch = pyglet.graphics.Batch()

pyglet.font.add_directory('fonts/')
press_start_2p_font = pyglet.font.load('Press Start 2P')

uptime_img      = pyglet.image.load('sprites/device.png')
cpu_usage_img   = pyglet.image.load('sprites/anger.png')
ram_usage_img   = pyglet.image.load('sprites/heart.png')
disk_usage_img  = pyglet.image.load('sprites/tiredness.png')
uptime_anim     = pyglet.image.load_animation('sprites/device_anim.gif')
cpu_usage_anim  = pyglet.image.load_animation('sprites/anger_anim.gif')
ram_usage_anim  = pyglet.image.load_animation('sprites/heart_anim.gif')
disk_usage_anim = pyglet.image.load_animation('sprites/tiredness_anim.gif')

bg_tile_img  = pyglet.image.load('sprites/bg_tile.png')
bg_tiles = [[pyglet.sprite.Sprite(bg_tile_img, x * bg_tile_img.width, y * bg_tile_img.height, batch = bg_batch) for x in range((1350 // bg_tile_img.width) + 2)] for y in range((window.height // bg_tile_img.height) + 1)]

ui_checkbox_empty_img   = pyglet.image.load('ui/checkbox_empty.png')
ui_checkbox_checked_img = pyglet.image.load('ui/checkbox_checked.png')
ui_nav_left_img         = pyglet.image.load('ui/nav_left.png')
ui_nav_right_img        = pyglet.image.load('ui/nav_right.png')
ui_settings_img         = pyglet.image.load('ui/settings_btn.png')

uptime_sprite          = pyglet.sprite.Sprite(uptime_img,      20, 440, batch = character_batch)
cpu_usage_sprite       = pyglet.sprite.Sprite(cpu_usage_img,   20, 300, batch = character_batch)
ram_usage_sprite       = pyglet.sprite.Sprite(ram_usage_img,   20, 160, batch = character_batch)
disk_usage_sprite      = pyglet.sprite.Sprite(disk_usage_img,  20, 20,  batch = character_batch)
uptime_anim_sprite     = pyglet.sprite.Sprite(uptime_anim,     20, 440, batch = anim_character_batch)
cpu_usage_anim_sprite  = pyglet.sprite.Sprite(cpu_usage_anim,  20, 300, batch = anim_character_batch)
ram_usage_anim_sprite  = pyglet.sprite.Sprite(ram_usage_anim,  20, 160, batch = anim_character_batch)
disk_usage_anim_sprite = pyglet.sprite.Sprite(disk_usage_anim, 20, 20,  batch = anim_character_batch)


def toggle_settings():
    global settings_shown

    settings_shown = not settings_shown
    if settings_shown: window.set_size(1350, window.get_size()[1])
    else: window.set_size(850, window.get_size()[1])

def save_settings():
    with open(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\settings.json', 'w') as file:
        dump(settings, file)

def set_animations_enabled(state):
    settings['enable_animations'] = state
    save_settings()
def set_bg_animation_enabled(state):
    settings['enable_bg_animation'] = state
    save_settings()
def set_blocks_transparency(state):
    settings['blocks_transparency'] = 204 if state else 255
    bg_resmon_main.color     = (255, 201, 201, settings['blocks_transparency'])
    bg_resmon_settings.color = (255, 201, 201, settings['blocks_transparency'])
    save_settings()
def set_shorter_update_interval(state):
    settings['shorter_update_interval'] = state
    save_settings()
def on_disk_nav_left():
    if settings['disk_index'] > 0: settings['disk_index'] -= 1
    else: settings['disk_index'] = 25
    save_settings()
def on_disk_nav_right():
    if settings['disk_index'] < 25: settings['disk_index'] += 1
    else: settings['disk_index'] = 0
    save_settings()


class Switch:

    def __init__(self, x: int, y: int, on_switch: Callable, state: bool = False) -> None:
        self.x = x
        self.y = y
        self.state = state
        self.on_switch = on_switch
        self.disabled_sprite = pyglet.sprite.Sprite(ui_checkbox_empty_img,   x, y)
        self.enabled_sprite  = pyglet.sprite.Sprite(ui_checkbox_checked_img, x, y)

    def click(self, x, y):
        if self.x <= x <= self.x + self.disabled_sprite.width and self.y <= y <= self.y + self.disabled_sprite.height:
            self.state = not self.state
            self.on_switch(self.state)

    def draw(self):
        if self.state: self.enabled_sprite.draw()
        else: self.disabled_sprite.draw()
    

class Button:

    def __init__(self, x: int, y: int, on_click: Callable, img) -> None:
        self.x = x
        self.y = y
        self.on_click = on_click
        self.sprite = pyglet.sprite.Sprite(img, x, y)

    def click(self, x, y):
        if self.x <= x <= self.x + self.sprite.width and self.y <= y <= self.y + self.sprite.height:
            self.on_click()

    def draw(self):
        self.sprite.draw()


ui = {
    'settings_toggle_button':  Button(790, 20, toggle_settings, ui_settings_img),
    'animations_switch':       Switch(860, window.height - 60, set_animations_enabled, settings['enable_animations']),
    'bg_animation_switch':     Switch(860, window.height - 110, set_bg_animation_enabled, settings['enable_bg_animation']),
    'transparency_switch':     Switch(860, window.height - 160, set_blocks_transparency, settings['blocks_transparency'] < 255),
    'disk_selector_nav_left':  Button(910, window.height - 260, on_disk_nav_left, ui_nav_left_img),
    'disk_selector_nav_right': Button(1010, window.height - 260, on_disk_nav_right, ui_nav_right_img),
    'update_interval_switch':  Switch(860, window.height - 335, set_shorter_update_interval, settings['shorter_update_interval']),
}


animations_setting_label = pyglet.text.Label(
    text      = 'Animations',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 910,
    y         = window.height - 40,
    anchor_y  = 'center',
    batch     = fg_batch
)
bg_animation_setting_label = pyglet.text.Label(
    text      = 'Animate background',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 910,
    y         = window.height - 90,
    anchor_y  = 'center',
    batch     = fg_batch
)
blocks_transparency_setting_label = pyglet.text.Label(
    text      = 'Transparent blocks',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 910,
    y         = window.height - 140,
    anchor_y  = 'center',
    batch     = fg_batch
)
disk_setting_label = pyglet.text.Label(
    text      = 'Disk letter',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 910,
    y         = window.height - 180,
    anchor_y  = 'top',
    batch     = fg_batch
)
disk_setting_letter = pyglet.text.Label(
    text      = 'C:',
    font_name = 'Press Start 2P',
    font_size = 24,
    color     = (255, 0, 201, 255),
    x         = 975,
    y         = window.height - 224,
    anchor_x  = 'center',
    anchor_y  = 'top',
    batch     = fg_batch
)
update_interval_label_1 = pyglet.text.Label(
    text      = 'Shorter update',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 910,
    y         = window.height - 300,
    anchor_y  = 'center',
    batch     = fg_batch
)
update_interval_label_2 = pyglet.text.Label(
    text      = 'interval',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 910,
    y         = window.height - 330,
    anchor_y  = 'center',
    batch     = fg_batch
)
uptime_title = pyglet.text.Label(
    text      = 'Uptime',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 570,
    anchor_y  = 'top',
    batch     = fg_batch
)
uptime_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 470,
    batch     = fg_batch
)
cpu_title = pyglet.text.Label(
    text      = 'CPU usage',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 430,
    anchor_y  = 'top',
    batch     = fg_batch
)
cpu_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 330,
    batch     = fg_batch
)
ram_title = pyglet.text.Label(
    text      = 'RAM usage',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 290,
    anchor_y  = 'top',
    batch     = fg_batch
)
ram_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 190,
    batch     = fg_batch
)
disk_title = pyglet.text.Label(
    text      = f'Used disk space ({ascii_uppercase[settings['disk_index']]}:)',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 150,
    anchor_y  = 'top',
    batch     = fg_batch
)
disk_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = (255, 0, 201, 255),
    x         = 200,
    y         = 50,
    batch     = fg_batch
)

bg_resmon_main = pyglet.shapes.Rectangle(
    x      = 10,
    y      = 10,
    width  = 830,
    height = 580,
    color  = (255, 201, 201, 255),
    batch  = bg_batch
)
bg_resmon_settings = pyglet.shapes.Rectangle(
    x      = 850,
    y      = 10,
    width  = 490,
    height = 580,
    color  = (255, 201, 201, 255),
    batch  = bg_batch
)


system_info = {
    'uptime': 'N/A',
    'cpu': 'N/A',
    'ram': 'N/A',
    'disk': 'N/A'
}

kernel32 = windll.kernel32


set_blocks_transparency(settings['blocks_transparency'] < 255)


@window.event
def on_draw():
    global bg_offset

    window.clear()

    if settings['enable_bg_animation']:
        bg_offset = (bg_offset - 1) % bg_tile_img.width
        for y in range(len(bg_tiles)):
            for x in range(len(bg_tiles[y])):
                bg_tiles[y][x].x = bg_offset + ((x - 1) * bg_tile_img.width)

    uptime_label.text = system_info['uptime']
    cpu_label.text = system_info['cpu']
    ram_label.text = system_info['ram']
    if forced_c_selection: disk_title.text = 'Used disk space (C:)'
    else: disk_title.text = f'Used disk space ({ascii_uppercase[settings['disk_index']]}:)'
    disk_setting_letter.text = f'{ascii_uppercase[settings['disk_index']]}:'
    disk_label.text = system_info['disk']

    bg_batch.draw()
    if settings['enable_animations']: anim_character_batch.draw()
    else: character_batch.draw()
    fg_batch.draw()

    for elem in ui:
        ui[elem].draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    for elem in ui:
        ui[elem].click(x, y)


def system_info_updater():
    global forced_c_selection

    while not pyglet.app.event_loop.is_running:
        print('pyglet evloop isn\'t running')
        sleep(50)
    while pyglet.app.event_loop.is_running:

        seconds_uptime = kernel32.GetTickCount64()
        seconds_uptime = int(str(seconds_uptime)[:-3])
        mins, sec = divmod(seconds_uptime, 60)
        hour, mins = divmod(mins, 60)
        system_info['uptime'] = f'{hour:02}:{mins:02}:{sec:02}'

        system_info['cpu'] = f'{szfill(round(cpu_percent(), 1))}%'

        system_info['ram'] = f'{szfill(round(virtual_memory().percent, 1))}%'

        try:
            c_usage = disk_usage(f'{ascii_uppercase[settings['disk_index']]}:\\')
            forced_c_selection = False
        except (FileNotFoundError, PermissionError):
            c_usage = disk_usage('C:\\')
            forced_c_selection = True
        system_info['disk'] = f'{szfill(round(c_usage.used / c_usage.total * 100, 1))}%'

        sleep(0.5 if settings['shorter_update_interval'] else 1)


system_info_updater_thread = Thread(target = system_info_updater, args = ())
system_info_updater_thread.start()

pyglet.app.run()