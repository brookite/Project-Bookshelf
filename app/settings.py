import os
import json
import re
import warnings
from zipfile import ZipFile
from typing import Union, List, Dict, Optional

DEFAULT_PATH = os.path.expanduser("~/.bookshelf")
if not os.path.exists(DEFAULT_PATH):
    os.mkdir(DEFAULT_PATH)

VARIABLE_PATTERN = r"\$([\w_]+)"


class BooksConfig(dict):
    def __init__(self, path: str):
        super().__init__()
        self._path = path
        self.load()
        self._create_structure()

    def _create_structure(self):
        self.setdefault("shelfs", [])
        if len(self["shelfs"]) == 0:
            self.add_shelf("$DEFAULT_NAME")
        self.save()

    def add_file(self, shelf_index: int, file: Union[os.PathLike, str]) -> Optional[dict]:
        for bookdata in self.get_books(shelf_index):
            if bookdata["src"] == os.path.abspath(file):
                return None
        book = {}
        book["name"] = os.path.basename(file)
        book["src"] = os.path.abspath(file)
        book["thumbnail"] = None
        book["openCount"] = 0
        self["shelfs"][shelf_index]["books"].append(book)
        self.save()
        return book

    def get_books(self, shelf_index: int) -> List[Dict]:
        return self["shelfs"][shelf_index]["books"]

    def remove_book(self, metadata: dict, shelf_index=None):
        if shelf_index is None:
            for shelf in self["shelfs"]:
                if metadata in shelf["books"]:
                    shelf["books"].remove(metadata)
        else:
            if metadata in self["shelfs"][shelf_index]["books"]:
                self["shelfs"][shelf_index]["books"].remove(metadata)
            else:
                warnings.warn("Book wasn't found in specified shelf")

    def add_shelf(self, name) -> int:
        shelf = {}
        shelf["name"] = name
        shelf["view"] = "default"
        shelf["books"] = []
        self["shelfs"].append(shelf)
        self.save()
        return len(self["shelfs"]) - 1, shelf

    def load(self):
        try:
            with open(self._path, "rb") as fobj:
                self.clear()
                self.update(json.load(fobj))
        except json.JSONDecodeError:
            self.save()

    def refresh(self):
        with open(self._path, "rb") as fobj:
            self.update(json.load(fobj))

    def save(self):
        with open(self._path, "w", encoding="utf-8") as fobj:
            json.dump(self, fobj, ensure_ascii=False, indent=4)

    def route(self, *args) -> Union[list, dict]:
        obj = self
        for arg in args:
            obj = obj[arg]
        return obj


class AppStorage:
    def __init__(self):
        self.root = DEFAULT_PATH
        self.create_files()
        self.config = BooksConfig(os.path.join(self.root, "books.json"))

    def backup(self, output_path):
        exclude = ["book_paths", ".thumbnails"]
        with ZipFile(output_path, 'w') as zipobj:
            for folder, subfolders, filenames in os.walk(self.root):
                for filename in filenames:
                    if not (os.path.basename(filename) in exclude
                            or os.path.basename(folder) in exclude):
                        filepath = os.path.join(folder, filename)
                        zippath = filepath.replace(self.root + os.sep, "")
                        zipobj.write(filepath, zippath)

    def restore(self, backup_path):
        # check that books.json in archive, clear storage, extract zip
        pass

    def resolve_env_variable(self, pattern):
        matches = re.finditer(VARIABLE_PATTERN, pattern)
        for match in matches:
            value = self.get_var(match.group(1))
            if value:
                pattern = pattern.replace(match.group(), value)
        return pattern

    def get_var(self, var):
        if var == "DEFAULT_THUMBNAIL_PATH":
            return self.thumbnail_dir
        elif var == "DEFAULT_USER_THUMBNAIL_PATH":
            return self.user_thumbnail_dir
        else:
            return os.getenv(var)

    def create_files(self):
        self.create_file_if_not_exists(self.root, "books.json")
        self.create_file_if_not_exists(self.root, "book_paths")
        self.create_dir_if_not_exists(self.root, ".user_thumbnails")
        self.create_dir_if_not_exists(self.root, ".thumbnails")
        self.create_dir_if_not_exists(self.root, "shelf_view")

    @staticmethod
    def create_file_if_not_exists(root, file):
        path = os.path.join(root, file)
        if not os.path.exists(path):
            open(path, "wb").close()

    @staticmethod
    def create_dir_if_not_exists(root, file):
        path = os.path.join(root, file)
        if not os.path.exists(path):
            os.mkdir(path)

    @property
    def thumbnail_dir(self) -> str:
        return os.path.join(self.root, ".thumbnails")

    @property
    def user_thumbnail_dir(self) -> str:
        return os.path.join(self.root, ".user_thumbnails")
