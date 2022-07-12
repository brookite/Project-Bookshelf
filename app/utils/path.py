import os


def resolve_path(*args):
    project_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(project_path, *args))
