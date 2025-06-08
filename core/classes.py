from ctypes import Structure, c_long


class Point(Structure):
    _fields_ = [
        ('x', c_long),
        ('y', c_long)
    ]