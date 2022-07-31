import os
import json
from typing import Union, List, Dict, Optional

DEFAULT_PATH = os.path.expanduser("~/.bookshelf")
if not os.path.exists(DEFAULT_PATH):
    os.mkdir(DEFAULT_PATH)


class BooksConfig(dict):
    def __init__(self, path):
        super().__init__()
        self._path = path
        self.load()
        self._create_structure()

    def _create_structure(self):
        self.setdefault("shelfs", [])
        if len(self["shelfs"]) == 0:
            self.add_shelf("DEFAULT_NAME")
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

    def add_shelf(self, name) -> int:
        shelf = {}
        shelf["name"] = name
        shelf["view"] = "default"
        shelf["books"] = []
        self["shelfs"].append(shelf)
        self.save()
        return len(self["shelfs"]) - 1

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
            json.dump(self, fobj, ensure_ascii=False)

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

    def create_files(self):
        self.create_file_if_not_exists(self.root, "books.json")
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

