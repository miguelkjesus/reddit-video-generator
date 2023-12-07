import os

def mkdir(path: str) -> str:
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def read(path: str, encoding: str = None):
    with open(path, "r", encoding=encoding) as f:
        return f.read()

def write(path: str, data: str, encoding: str = None):
    with open(path, "w", encoding=encoding) as f:
        f.write(data)