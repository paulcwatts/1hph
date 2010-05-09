import os.path

ROOT = os.path.abspath(os.path.dirname(__file__))

def open_file(path):
    return open(os.path.join(ROOT, path))

def get_file_path(path):
    return os.path.join(ROOT, path)
