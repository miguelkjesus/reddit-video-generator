import os
from math import log, floor

def mkdir(path: str) -> str:
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def human_format(number: float | int, dp: int = 1) -> str:
    if number < 1000 and floor(number) == number:
        return str(int(floor(number)))
    
    units = ['', 'k', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return f'%.{dp}f%s' % (number / k**magnitude, units[magnitude])