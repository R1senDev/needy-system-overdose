from webbrowser import open as open_url
from traceback  import format_exc
from threading  import Thread
from getpass    import getuser
from psutil     import cpu_percent, virtual_memory, disk_usage
from ctypes     import windll, Structure, c_long, byref
from string     import ascii_uppercase
from typing     import Callable
from random     import choice
from json       import load, dump
from time       import sleep
from os         import makedirs

import pyglet


WIDE_WINDOW_WIDTH = 1350
BASE_WINDOW_WIDTH = 850

CPU_PBAR_WARN  = 0.85
RAM_PBAR_WARN  = 0.85
DISK_PBAR_WARN = 0.9

COL_LIGHT_PINK_BG = (255, 204, 204, 255)
COL_PINK_TEXT     = (255,  51, 204, 255)
COL_ACCENT        = (255, 153, 204, 255)
COL_NORM_VALUE    = (255,   0, 204, 255)
COL_CRIT_VALUE    = (255,   0, 102, 255)

dragging_window    = [False, 0, 0]
settings_shown     = False
forced_c_selection = False
dialog_is_opened   = False

bg_offset = 0


default_settings = {
    'enable_animations': True,
    'disk_index': 2,
    'shorter_update_interval': False,
    'enable_bg_animation': False,
    'blocks_transparency': 255,
    'disk_space_variant': 'used',
    'random_sprites_pack': False,
    'custom_cursor': False,
    'show_units': False,
}
try:
    makedirs(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\')
    settings = default_settings
    with open(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\settings.json', 'w') as file:
        dump(default_settings, file)
except OSError:
    with open(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\settings.json', 'r') as file:
        settings = load(file)
    for key in default_settings:
        if key not in settings:
            settings = default_settings
            with open(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\settings.json', 'w') as file:
                dump(default_settings, file)
            break

with open('sprites/packs_data.json', 'r') as packs_data_file:
    packs_data = load(packs_data_file)


def szfill(num: int | float | str, before_dot: int = 2) -> str:
    num = str(num)
    if '100' in num.split('.'): return '100 '
    while len(num.split('.')[0]) < before_dot: num = f'0{num}'
    return num


class Point(Structure):
    _fields_ = [
        ('x', c_long),
        ('y', c_long)
    ]


def get_absolute_cursor_position() -> list[int]:
    point = Point()
    windll.user32.GetCursorPos(byref(point))
    return [point.x, point.y]

try:
    screen = pyglet.display.get_display().get_default_screen()
    window = pyglet.window.Window(
        width     = BASE_WINDOW_WIDTH,
        height    = 670,
        resizable = False,
        style     = 'borderless',
        caption   = 'NeedySystemOverdose'
    )
except Exception:
    print('Oh no! It seems that you have an outdated driver (for example, the Intel HD Graphics 2046). Full traceback is in the crash.log file.')
    with open('crash.log', 'w') as crash_log:
        crash_log.write(format_exc())
    exit()

window.set_location(screen.width // 2 - WIDE_WINDOW_WIDTH // 2, screen.height // 2 - window.height // 2)


bg_batch             = pyglet.graphics.Batch()
fg_batch             = pyglet.graphics.Batch()
dialog_bg_batch      = pyglet.graphics.Batch()
dialog_fg_batch      = pyglet.graphics.Batch()
character_batch      = pyglet.graphics.Batch()
anim_character_batch = pyglet.graphics.Batch()

# Loading font
pyglet.font.add_directory('fonts/')
press_start_2p_font = pyglet.font.load('Press Start 2P')

if settings['random_sprites_pack']: pack = choice(packs_data)
else: pack = packs_data[0]

# Loading characters' sprites
uptime_img      = pyglet.image.load(f'sprites/characters/{pack["uptime"]["static"]}')
cpu_usage_img   = pyglet.image.load(f'sprites/characters/{pack["cpu"]["static"]}')
ram_usage_img   = pyglet.image.load(f'sprites/characters/{pack["ram"]["static"]}')
disk_usage_img  = pyglet.image.load(f'sprites/characters/{pack["disk"]["static"]}')
uptime_anim     = pyglet.image.load_animation(f'sprites/characters/{pack["uptime"]["animated"]}')
cpu_usage_anim  = pyglet.image.load_animation(f'sprites/characters/{pack["cpu"]["animated"]}')
ram_usage_anim  = pyglet.image.load_animation(f'sprites/characters/{pack["ram"]["animated"]}')
disk_usage_anim = pyglet.image.load_animation(f'sprites/characters/{pack["disk"]["animated"]}')
question_anim   = pyglet.image.load_animation('sprites/characters/question_anim.gif')

# Loading cursors' sprites
cur_normal_img  = pyglet.image.load('cursors/cursor_normal.png')
cur_pointer_img = pyglet.image.load('cursors/cursor_pointer.png')

# Gathering default OS cursor
cur_default_normal  = window.CURSOR_DEFAULT
# Creating cursors from sprites
cur_normal  = pyglet.window.ImageMouseCursor(cur_normal_img, 0, cur_normal_img.height)
cur_pointer = pyglet.window.ImageMouseCursor(cur_pointer_img, 9, cur_pointer_img.height)
window.set_mouse_cursor(cur_normal)

icon32_img  = pyglet.image.load('sprites/icon32.png')
icon64_img  = pyglet.image.load('sprites/icon64.png')
icon128_img = pyglet.image.load('sprites/icon128.png')
window.set_icon(icon32_img, icon64_img, icon128_img)

bg_tile_img  = pyglet.image.load('sprites/bg_tile.png')
bg_tiles = [[pyglet.sprite.Sprite(bg_tile_img, x * bg_tile_img.width, y * bg_tile_img.height, batch = bg_batch) for x in range((WIDE_WINDOW_WIDTH // bg_tile_img.width) + 2)] for y in range((window.height // bg_tile_img.height) + 1)]

ui_close_img            = pyglet.image.load('ui/close_btn.png')
ui_confirm_img          = pyglet.image.load('ui/confirm_btn.png')
ui_cancel_img           = pyglet.image.load('ui/cancel_btn.png')
ui_minimize_img         = pyglet.image.load('ui/minimize_btn.png')
ui_checkbox_empty_img   = pyglet.image.load('ui/checkbox_empty.png')
ui_checkbox_checked_img = pyglet.image.load('ui/checkbox_checked.png')
ui_nav_left_img         = pyglet.image.load('ui/nav_left.png')
ui_nav_right_img        = pyglet.image.load('ui/nav_right.png')
ui_settings_img         = pyglet.image.load('ui/settings_btn.png')
ui_link_img             = pyglet.image.load('ui/link_btn.png')

icon_sprite            = pyglet.sprite.Sprite(icon64_img,      20, window.height - 72,  batch = fg_batch)
uptime_sprite          = pyglet.sprite.Sprite(uptime_img,      20, 440,                 batch = character_batch)
cpu_usage_sprite       = pyglet.sprite.Sprite(cpu_usage_img,   20, 300,                 batch = character_batch)
ram_usage_sprite       = pyglet.sprite.Sprite(ram_usage_img,   20, 160,                 batch = character_batch)
disk_usage_sprite      = pyglet.sprite.Sprite(disk_usage_img,  20, 20,                  batch = character_batch)
uptime_anim_sprite     = pyglet.sprite.Sprite(uptime_anim,     20, 440,                 batch = anim_character_batch)
cpu_usage_anim_sprite  = pyglet.sprite.Sprite(cpu_usage_anim,  20, 300,                 batch = anim_character_batch)
ram_usage_anim_sprite  = pyglet.sprite.Sprite(ram_usage_anim,  20, 160,                 batch = anim_character_batch)
disk_usage_anim_sprite = pyglet.sprite.Sprite(disk_usage_anim, 20, 20,                  batch = anim_character_batch)
question_anim_sprite   = pyglet.sprite.Sprite(question_anim,   30, window.height - 195, batch = dialog_fg_batch)

uptime_anim_sprite.frame_index = 0
cpu_usage_anim_sprite.frame_index = 0
ram_usage_anim_sprite.frame_index = 0
disk_usage_anim_sprite.frame_index = 0
question_anim_sprite.frame_index = 0

def toggle_settings():
    global settings_shown

    settings_shown = not settings_shown
    if settings_shown: window.set_size(WIDE_WINDOW_WIDTH, window.get_size()[1])
    else: window.set_size(BASE_WINDOW_WIDTH, window.get_size()[1])

def save_settings():
    with open(f'C:\\Users\\{getuser()}\\AppData\\Local\\R1senDev\\NeedySys\\settings.json', 'w') as file:
        dump(settings, file)

def on_close_button_press():
    global dialog_is_opened
    dialog_is_opened = True

def close_dialog():
    global dialog_is_opened
    dialog_is_opened = False

def set_animations_enabled(state):
    settings['enable_animations'] = state
    save_settings()

def set_bg_animation_enabled(state):
    settings['enable_bg_animation'] = state
    save_settings()

def set_blocks_transparency(state):
    settings['blocks_transparency'] = 204 if state else 255
    bg_resmon_header.color   = (255, 204, 204, settings['blocks_transparency'])
    bg_resmon_main.color     = (255, 204, 204, settings['blocks_transparency'])
    bg_resmon_info.color     = (255, 204, 204, settings['blocks_transparency'])
    bg_resmon_settings.color = (255, 204, 204, settings['blocks_transparency'])
    save_settings()

def set_shorter_update_interval(state):
    settings['shorter_update_interval'] = state
    save_settings()

def set_disk_space_variant_to_free(state):
    settings['disk_space_variant'] = 'free' if state else 'used'
    save_settings()

def set_randomize_sprites_packs(state):
    settings['random_sprites_pack'] = state
    save_settings()

def set_custom_cursor(state):
    settings['custom_cursor'] = not state
    if state:
        window.set_mouse_cursor(cur_default_normal)
    else:
        window.set_mouse_cursor(cur_pointer)
    save_settings()

def set_show_units(state):
    settings['show_units'] = state
    save_settings()

def on_disk_nav_left():
    if settings['disk_index'] > 0:
        settings['disk_index'] -= 1
    else:
        settings['disk_index'] = 25
    save_settings()

def on_disk_nav_right():
    if settings['disk_index'] < 25:
        settings['disk_index'] += 1
    else:
        settings['disk_index'] = 0
    save_settings()

def open_github_repo():
    open_url('https://github.com/R1senDev/needy-system-overdose', 2)


class Progress:

    def __init__(self, x: int, y: int, w: int, h: int, bg_color: tuple[int, int, int, int] = (255, 255, 255, 255), fill_color: tuple[int, int, int, int] = (0, 255, 0, 255), progress: float = 0.0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.progress = progress

        self.bg_rect = pyglet.shapes.Rectangle(
            x      = self.x,
            y      = self.y,
            width  = self.w,
            height = self.h,
            color  = self.bg_color,
            batch  = fg_batch
        )
        self.fill_rect = pyglet.shapes.Rectangle(
            x      = self.x,
            y      = self.y,
            width  = round(self.w * self.progress),
            height = self.h,
            color  = self.fill_color,
            batch  = fg_batch
        )

    def update_progress(self, progress):
        self.fill_rect.width = round(self.w * progress)

    def update_fill_color(self, color):
        self.fill_rect.color = color

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
            return True
        return False

    def draw(self):
        if self.state:
            self.enabled_sprite.draw()
        else:
            self.disabled_sprite.draw()

    def is_inner(self, x: int, y: int) -> bool:
        return self.x <= x <= self.x + self.disabled_sprite.width and self.y <= y <= self.y + self.disabled_sprite.height
    

class Button:

    def __init__(self, x: int, y: int, on_click: Callable, img) -> None:
        self.x = x
        self.y = y
        self.on_click = on_click
        self.sprite = pyglet.sprite.Sprite(img, x, y)

    def click(self, x, y) -> bool:
        if self.x <= x <= self.x + self.sprite.width and self.y <= y <= self.y + self.sprite.height:
            self.on_click()
            return True
        return False

    def draw(self):
        self.sprite.draw()
    
    def is_inner(self, x: int, y: int) -> bool:
        return self.x <= x <= self.x + self.sprite.width and self.y <= y <= self.y + self.sprite.height


ui = {
    'window_close_button':         Button(BASE_WINDOW_WIDTH - 60,  window.height - 60, on_close_button_press, ui_close_img),
    'window_minimize_button':      Button(BASE_WINDOW_WIDTH - 110, window.height - 60, window.minimize, ui_minimize_img),
    'settings_toggle_button':      Button(790,  20,  toggle_settings, ui_settings_img),
    'github_link':                 Button(1290, 610, open_github_repo, ui_link_img),
    'animations_switch':           Switch(860,  540, set_animations_enabled, settings['enable_animations']),
    'bg_animation_switch':         Switch(860,  490, set_bg_animation_enabled, settings['enable_bg_animation']),
    'transparency_switch':         Switch(860,  440, set_blocks_transparency, settings['blocks_transparency'] < 255),
    'disk_selector_nav_left':      Button(910,  340, on_disk_nav_left, ui_nav_left_img),
    'disk_selector_nav_right':     Button(1010, 340, on_disk_nav_right, ui_nav_right_img),
    'update_interval_switch':      Switch(860,  265, set_shorter_update_interval, settings['shorter_update_interval']),
    'disk_space_variant_switch':   Switch(860,  185, set_disk_space_variant_to_free, settings['disk_space_variant'] == 'free'),
    'random_sprites_pack_switch':  Switch(860,  120, set_randomize_sprites_packs, settings['random_sprites_pack']),
    'custom_cursor_switch':        Switch(860,  70,  set_custom_cursor, not settings['custom_cursor']),
    'show_units':                  Switch(860,  20,  set_show_units, settings['show_units']),
}

dialog_ui = {
    'confirm_button': Button(BASE_WINDOW_WIDTH - 80,  window.height - 170, window.close, ui_confirm_img),
    'cancel_button':  Button(BASE_WINDOW_WIDTH - 130, window.height - 170, close_dialog, ui_cancel_img),
}

other_elements = {
    'cpu_progress':  Progress(200, 320, 325, 10, COL_ACCENT, COL_NORM_VALUE),
    'ram_progress':  Progress(200, 180, 325, 10, COL_ACCENT, COL_NORM_VALUE),
    'disk_progress': Progress(200, 40,  325, 10, COL_ACCENT, COL_NORM_VALUE),
}

window_title = pyglet.text.Label(
    text      = 'NeedySystemOverdose',
    font_name = 'Press Start 2P',
    font_size = 16,
    italic    = True,
    color     = COL_NORM_VALUE,
    x         = 94,
    y         = window.height - 40,
    anchor_y  = 'center',
    batch     = fg_batch
)
window_title_version = pyglet.text.Label(
    text      = 'v1.3.1b',
    font_name = 'Press Start 2P',
    font_size = 10,
    color     = COL_PINK_TEXT,
    x         = BASE_WINDOW_WIDTH - 120,
    y         = window.height - 60,
    anchor_x  = 'right',
    anchor_y  = 'bottom',
    batch     = fg_batch
)

info_label = pyglet.text.Label(
    text      = 'project by R1senDev',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 860,
    y         = 630,
    anchor_y  = 'center',
    batch     = fg_batch
)
animations_setting_label = pyglet.text.Label(
    text      = 'Animations',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 560,
    anchor_y  = 'center',
    batch     = fg_batch
)
bg_animation_setting_label = pyglet.text.Label(
    text      = 'Animate background',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 510,
    anchor_y  = 'center',
    batch     = fg_batch
)
blocks_transparency_setting_label = pyglet.text.Label(
    text      = 'Transparent blocks',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 460,
    anchor_y  = 'center',
    batch     = fg_batch
)
disk_setting_label = pyglet.text.Label(
    text      = 'Disk letter',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 420,
    anchor_y  = 'top',
    batch     = fg_batch
)
disk_setting_letter = pyglet.text.Label(
    text      = 'C:',
    font_name = 'Press Start 2P',
    font_size = 24,
    color     = COL_NORM_VALUE,
    x         = 975,
    y         = 376,
    anchor_x  = 'center',
    anchor_y  = 'top',
    batch     = fg_batch
)
update_interval_label_1 = pyglet.text.Label(
    text      = 'Shorter update',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 300,
    anchor_y  = 'center',
    batch     = fg_batch
)
update_interval_label_2 = pyglet.text.Label(
    text      = 'interval',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 270,
    anchor_y  = 'center',
    batch     = fg_batch
)
show_free_space_label_1 = pyglet.text.Label(
    text      = 'Show free disk space',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 220,
    anchor_y  = 'center',
    batch     = fg_batch
)
show_free_space_label_2 = pyglet.text.Label(
    text      = 'instead of used',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 190,
    anchor_y  = 'center',
    batch     = fg_batch
)
randomize_packs_label = pyglet.text.Label(
    text      = 'Random sprites pack',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 140,
    anchor_y  = 'center',
    batch     = fg_batch
)
default_cursor_label = pyglet.text.Label(
    text      = 'Default cursor',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 90,
    anchor_y  = 'center',
    batch     = fg_batch
)
show_units_label = pyglet.text.Label(
    text      = 'Show units',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_NORM_VALUE,
    x         = 910,
    y         = 40,
    anchor_y  = 'center',
    batch     = fg_batch
)

uptime_title = pyglet.text.Label(
    text      = 'Uptime',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_PINK_TEXT,
    x         = 200,
    y         = 570,
    anchor_y  = 'top',
    batch     = fg_batch
)
uptime_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = COL_NORM_VALUE,
    x         = 200,
    y         = 470,
    batch     = fg_batch
)
cpu_title = pyglet.text.Label(
    text      = 'CPU usage',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_PINK_TEXT,
    x         = 200,
    y         = 430,
    anchor_y  = 'top',
    batch     = fg_batch
)
cpu_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = COL_NORM_VALUE,
    x         = 200,
    y         = 330,
    batch     = fg_batch
)
ram_title = pyglet.text.Label(
    text      = 'RAM usage',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_PINK_TEXT,
    x         = 200,
    y         = 290,
    anchor_y  = 'top',
    batch     = fg_batch
)
ram_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = COL_NORM_VALUE,
    x         = 200,
    y         = 190,
    batch     = fg_batch
)
disk_title = pyglet.text.Label(
    text      = f'{"Free" if settings["disk_space_variant"] == "free" else "Used"} disk space ({ascii_uppercase[settings["disk_index"]]}:)',
    font_name = 'Press Start 2P',
    font_size = 16,
    color     = COL_PINK_TEXT,
    x         = 200,
    y         = 150,
    anchor_y  = 'top',
    batch     = fg_batch
)
disk_label = pyglet.text.Label(
    text      = 'N/A',
    font_name = 'Press Start 2P',
    font_size = 50,
    color     = COL_NORM_VALUE,
    x         = 200,
    y         = 50,
    batch     = fg_batch
)

bg_resmon_header = pyglet.shapes.Rectangle(
    x      = 10,
    y      = window.height - 70,
    width  = 830,
    height = 60,
    color  = COL_LIGHT_PINK_BG,
    batch  = bg_batch
)
bg_resmon_main = pyglet.shapes.Rectangle(
    x      = 10,
    y      = 10,
    width  = 830,
    height = 580,
    color  = COL_LIGHT_PINK_BG,
    batch  = bg_batch
)
bg_resmon_info = pyglet.shapes.Rectangle(
    x      = BASE_WINDOW_WIDTH,
    y      = window.height - 70,
    width  = 490,
    height = 60,
    color  = COL_LIGHT_PINK_BG,
    batch  = bg_batch
)
bg_resmon_settings = pyglet.shapes.Rectangle(
    x      = BASE_WINDOW_WIDTH,
    y      = 10,
    width  = 490,
    height = 580,
    color  = COL_LIGHT_PINK_BG,
    batch  = bg_batch
)


dialog_dark_overlay = pyglet.shapes.Rectangle(
    x      = 0,
    y      = 0,
    width  = WIDE_WINDOW_WIDTH,
    height = window.height,
    color  = (0, 0, 0, 153),
    batch  = dialog_bg_batch
)
dialog_outer_container = pyglet.shapes.Rectangle(
    x      = 20,
    y      = window.height - 190,
    width  = BASE_WINDOW_WIDTH - 40,
    height = 100,
    color  = COL_PINK_TEXT,
    batch  = dialog_bg_batch
)
dialog_inner_container = pyglet.shapes.Rectangle(
    x      = dialog_outer_container.x + 5,
    y      = dialog_outer_container.y + 5,
    width  = dialog_outer_container.width - 10,
    height = dialog_outer_container.height - 10,
    color  = COL_LIGHT_PINK_BG,
    batch  = dialog_bg_batch
)
dialog_label = pyglet.text.Label(
    text      = 'Are you sure you want to exit?',
    font_name = 'Press Start 2P',
    font_size = 14,
    color     = COL_NORM_VALUE,
    x         = dialog_inner_container.x + dialog_inner_container.width - 10,
    y         = dialog_inner_container.y + dialog_inner_container.height - 10,
    anchor_x  = 'right',
    anchor_y  = 'top',
    batch     = dialog_fg_batch
)


system_info = {
    'uptime':    'N/A',
    'cpu':       'N/A',
    'ram':       'N/A',
    'ram_used':  'N/A',
    'ram_total': 'N/A',
    'disk':      'N/A',
    'disk_used': 'N/A'
}

raw_system_info = {
    'uptime':          -1.0,
    'cpu':             -1.0,
    'ram':             -1.0,
    'used_disk_space': -1.0
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
        
    if dragging_window[0]:
        current_window_position = window.get_location()
        current_cursor_position = get_absolute_cursor_position()
        window.set_location(
            current_window_position[0] + current_cursor_position[0] - dragging_window[1],
            current_window_position[1] + current_cursor_position[1] - dragging_window[2]
        )
        dragging_window[1], dragging_window[2] = current_cursor_position[0], current_cursor_position[1]

    uptime_label.text = system_info['uptime']
    cpu_label.text = system_info['cpu']
    if not settings['show_units']:
        ram_label.text = system_info['ram']
    else:
        ram_label.text = f'{system_info["ram_used"]}/{system_info["ram_total"]}GB'
    if forced_c_selection:
        disk_title.text = 'Used disk space (C:)'
    else:
        disk_title.text = f'{"Free" if settings["disk_space_variant"] == "free" else "Used"} disk space ({ascii_uppercase[settings["disk_index"]]}:)'
    disk_setting_letter.text = f'{ascii_uppercase[settings["disk_index"]]}:'
    if not settings['show_units']:
        disk_label.text = system_info['disk']
    else:
        disk_label.text = f'{system_info["disk_used"]}GB' if raw_system_info["disk_used"] < 1024 else f'{round(raw_system_info["disk_used"] / 1024, 1)}TB'

    if raw_system_info['cpu'] < CPU_PBAR_WARN:
        cpu_label.color = COL_NORM_VALUE
    else:
        cpu_label.color = COL_CRIT_VALUE
    if raw_system_info['ram'] < RAM_PBAR_WARN:
        ram_label.color = COL_NORM_VALUE
    else:
        ram_label.color = COL_CRIT_VALUE
    if raw_system_info['used_disk_space'] < DISK_PBAR_WARN:
        disk_label.color = COL_NORM_VALUE
    else:
        disk_label.color = COL_CRIT_VALUE

    bg_batch.draw()
    if settings['enable_animations']:
        anim_character_batch.draw()
    else:
        character_batch.draw()
    fg_batch.draw()

    for elem in ui:
        ui[elem].draw()

    if dialog_is_opened:
        dialog_bg_batch.draw()
        dialog_fg_batch.draw()
        for elem in dialog_ui:
            dialog_ui[elem].draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    global dragging_window, dialog_is_opened

    interaction = False

    if not dialog_is_opened:
        for elem in ui:
            interaction = interaction or ui[elem].click(x, y)
    else:
        if not (dialog_outer_container.x <= x <= dialog_outer_container.x + dialog_outer_container.width and dialog_outer_container.y <= y <= dialog_outer_container.y + dialog_outer_container.height):
            dialog_is_opened = False
        else:
            for elem in dialog_ui:
                interaction = interaction or dialog_ui[elem].click(x, y)

    if not interaction:
        dragging_window = [True, *get_absolute_cursor_position()]

@window.event
def on_mouse_release(x, y, button, modifiers):
    global dragging_window
    dragging_window[0] = False


@window.event
def on_mouse_motion(x, y, *args, **kwargs):
    if settings['custom_cursor']:
        need_to_ask_interation = False
        for elem in ui:
            need_to_ask_interation = need_to_ask_interation or ui[elem].is_inner(x, y)
        window.set_mouse_cursor(cur_pointer if need_to_ask_interation else cur_normal)
    else:
        window.set_mouse_cursor(cur_default_normal)


def system_info_updater():
    global forced_c_selection

    while not pyglet.app.event_loop.is_running:
        sleep(0.02)
    while pyglet.app.event_loop.is_running:

        seconds_uptime = kernel32.GetTickCount64()
        seconds_uptime = int(str(seconds_uptime)[:-3])
        mins, sec = divmod(seconds_uptime, 60)
        hour, mins = divmod(mins, 60)
        system_info['uptime'] = f'{hour:02}:{mins:02}:{sec:02}'
        raw_system_info['uptime'] = seconds_uptime

        cpu_usage = cpu_percent()
        system_info['cpu'] = f'{szfill(round(cpu_usage, 1))}%'
        raw_system_info['cpu'] = cpu_usage / 100
        other_elements['cpu_progress'].update_progress(cpu_usage / 100)
        if cpu_usage / 100 >= CPU_PBAR_WARN:
            other_elements['cpu_progress'].update_fill_color(COL_CRIT_VALUE)
        else:
            other_elements['cpu_progress'].update_fill_color(COL_NORM_VALUE)

        vmem_usage = virtual_memory().percent
        system_info['ram'] = f'{szfill(round(vmem_usage, 1))}%'
        raw_system_info['ram'] = vmem_usage / 100
        system_info['ram_used']  = str(round(virtual_memory().used / 1024 / 1024 / 1024, 1))
        system_info['ram_total'] = str(round(virtual_memory().total / 1024 / 1024 / 1024, 1)).rstrip('.0')
        other_elements['ram_progress'].update_progress(vmem_usage / 100)
        if vmem_usage / 100 >= RAM_PBAR_WARN:
            other_elements['ram_progress'].update_fill_color(COL_CRIT_VALUE)
        else:
            other_elements['ram_progress'].update_fill_color(COL_NORM_VALUE)

        try:
            c_usage = disk_usage(f'{ascii_uppercase[settings["disk_index"]]}:\\')
            forced_c_selection = False
        except (FileNotFoundError, PermissionError):
            c_usage = disk_usage('C:\\')
            forced_c_selection = True
        system_info['disk_used'] = str(round(c_usage.used / 1024 / 1024 / 1024, 1))
        if settings['disk_space_variant'] == 'used':
            system_info['disk'] = f'{szfill(round(c_usage.used / c_usage.total * 100, 1))}%'
        else:
            system_info['disk'] = f'{szfill(round(c_usage.free / c_usage.total * 100, 1))}%'
        raw_system_info['used_disk_space'] = c_usage.used / c_usage.total
        other_elements['disk_progress'].update_progress(c_usage.used / c_usage.total)
        if c_usage.used / c_usage.total >= DISK_PBAR_WARN:
            other_elements['disk_progress'].update_fill_color(COL_CRIT_VALUE)
        else:
            other_elements['disk_progress'].update_fill_color(COL_NORM_VALUE)

        sleep(0.5 if settings['shorter_update_interval'] else 1)


system_info_updater_thread = Thread(
    target = system_info_updater,
    args   = (),
    name   = 'SystemInfoUpdater',
    daemon = True
)
system_info_updater_thread.start()

pyglet.app.run()