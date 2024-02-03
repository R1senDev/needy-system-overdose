from os.path import exists
from json    import load


def assets_test():
    try:
        # Fonts
        assert exists('fonts/PressStart2P.ttf')

        # Global sprites
        assert exists('sprites/bg_tile.png')
        assert exists('sprites/icon32.png')
        assert exists('sprites/icon64.png')
        assert exists('sprites/icon128.png')

        # Fetching characters' sprites data
        with open('sprites/packs_data.json', 'r') as packs_data_file:
            packs_data = load(packs_data_file)

        # Characters' sprites
        for pack in packs_data:
            for view in pack:
                assert exists(f'sprites/characters/{pack[view]["static"]}')
                assert exists(f'sprites/characters/{pack[view]["animated"]}')

        # UI elements' sprites
        assert exists('ui/checkbox_checked.png')
        assert exists('ui/checkbox_empty.png')
        assert exists('ui/close_btn.png')
        assert exists('ui/link_btn.png')
        assert exists('ui/minimize_btn.png')
        assert exists('ui/nav_left.png')
        assert exists('ui/nav_right.png')
        assert exists('ui/settings_btn.png')
    
    except AssertionError:
        exit(1)


assets_test()
exit(0)