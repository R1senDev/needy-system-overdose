from os.path import join, isdir
from json    import load
from os      import listdir


class CharacterData:

    def __init__(self, name: str, reg_name: str, fallback: 'CharacterData | None') -> None:

        self.name = name
        self.reg_name = reg_name
        self.fallback = fallback

    def __repr__(self) -> str:

        result = f'{self.name} ({self.reg_name}'
        if self.fallback is not None:
            result += f', fallback: {self.fallback.name}'
        result += ')'

        return result


def get_characters() -> list[CharacterData]:

    result: list[CharacterData] = []

    for character in listdir('characters'):

        if character.startswith('_'):
            continue

        meta_path = join('characters', character, 'meta.json')

        print(f'Reading meta for {character}: {meta_path}')

        with open(meta_path) as meta_file:
            character_meta = load(meta_file)

        character_meta['reg_name'] = character

        result.append(CharacterData(**character_meta))

    return result