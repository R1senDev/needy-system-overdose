class UtilitaryClass:
    def __init__(self) -> None:
        raise RuntimeError(f'{self.__class__.__name__} class is utilitary and should not be instantiated. Consider using its @classmethods.')