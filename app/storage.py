import os
import json
import re
import shutil
import time
import traceback
import warnings
from zipfile import ZipFile
from typing import Union, List, Dict, Optional, Tuple

from app.appinfo import BUILD_NUMBER
from app.utils.path import SUPPORTED_IMAGES, commonpath

DEFAULT_PATH = os.path.expanduser("~/.bookshelf")
if not os.path.exists(DEFAULT_PATH):
    os.mkdir(DEFAULT_PATH)

VARIABLE_PATTERN = r"\$([\w_]+)"


class BooksConfig(dict):
    def __init__(self, storage: "AppStorage", path: str):
        super().__init__()
        self._storage = storage
        self._path = path
        self.load()
        self._create_structure()

    def _create_structure(self):
        self.setdefault("updated", int(time.time()))
        self.setdefault("defaultShelf", 0)
        self.setdefault("storeThumbnails", False)
        self.setdefault("bookShadows", True)
        self.setdefault("recoverAutobackup", False)
        self.setdefault("autobackupPath", "")
        self.setdefault("denyBookPaths", False)
        self.setdefault("shelfs", [])
        if len(self["shelfs"]) == 0:
            self.add_shelf("$DEFAULT_NAME")
        self.save()

    def move_shelfs(self, from_, to):
        i = self["defaultShelf"]
        defaultShelf = self["shelfs"][i]
        self["shelfs"].insert(to, self["shelfs"].pop(from_))
        self["defaultShelf"] = self["shelfs"].index(defaultShelf)

    def add_file(self, shelf_index: int, file: Union[os.PathLike, str]) -> Optional[dict]:
        for bookdata in self.get_books(shelf_index):
            if self.booksrc(bookdata) == os.path.abspath(file):
                return None
        book = {}
        book["name"] = os.path.basename(file)
        book["src"] = self._storage.to_book_path(file)
        book["thumbnail"] = None
        book["openCount"] = 0
        book["mark"] = None
        self["shelfs"][shelf_index]["books"].append(book)
        self.save()
        return book

    def uses_book_paths(self):
        for shelf in self["shelfs"]:
            for book in shelf["books"]:
                if self._storage.is_ambiguous_pattern(book["src"]):
                    return True
        return False

    def get_books(self, shelf_index: int) -> List[Dict]:
        return self["shelfs"][shelf_index]["books"]

    def booksrc(self, metadata):
        return self._storage.resolve_env_path(metadata["src"])

    def convert_to_bookpaths(self):
        for shelf in self["shelfs"]:
            for book in shelf["books"]:
                book["src"] = self._storage.to_book_path(self.booksrc(book))

    def convert_to_explicit_paths(self):
        for shelf in self["shelfs"]:
            for book in shelf["books"]:
                book["src"] = self.booksrc(book)

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

    def shelf_names_list(self) -> List[str]:
        names = []
        for shelf in self["shelfs"]:
            names.append(shelf["name"])
        return names

    def add_shelf(self, name) -> Tuple[int, dict]:
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
        self["app_version"] = BUILD_NUMBER
        self["updated"] = int(time.time())
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
        self.config = BooksConfig(self, os.path.join(self.root, "books.json"))
        self.book_paths: List[str] = self._read_book_paths()

    def shelf_view_path(self, index) -> Optional[str]:
        shelf = self.config["shelfs"][index]
        view = shelf["view"]
        if view != "default":
            path = os.path.join(self.root, "shelf_view", view)
            if os.path.exists(path):
                return path

    def shelf_views(self) -> List[str]:
        paths = []
        viewspath = os.path.join(self.root, "shelf_view")
        for file in os.listdir(viewspath):
            path = os.path.join(viewspath, file)
            ext = os.path.splitext(path)[1]
            if os.path.isfile(path) and ext in SUPPORTED_IMAGES:
                paths.append(path)
        return paths

    def _read_book_paths(self) -> List[str]:
        with open(
                os.path.join(self.root, "book_paths"),
                "r", encoding="utf-8") as fobj:
            s = fobj.read().strip()
            if s:
                return s.split("\n")
            else:
                return []

    def _write_book_paths(self) -> None:
        with open(
                os.path.join(self.root, "book_paths"),
                "w", encoding="utf-8") as fobj:
            fobj.write("\n".join(self.book_paths))

    def save(self):
        self.config.save()
        self._write_book_paths()

    def backup(self, output_path, save_thumbnails=False) -> None:
        exclude = [".thumbnails"] if not save_thumbnails else []
        with ZipFile(output_path, 'w') as zipobj:
            for folder, subfolders, filenames in os.walk(self.root):
                for filename in filenames:
                    if not (os.path.basename(filename) in exclude
                            or os.path.basename(folder) in exclude):
                        filepath = os.path.join(folder, filename)
                        zippath = filepath.replace(self.root + os.sep, "")
                        zipobj.write(filepath, zippath)

    def restore(self, backup_path, save_thumbnails=False) -> bool:
        oldBackupPath = self.config["autobackupPath"]
        try:
            if commonpath(
                    [os.path.abspath(backup_path), self.root]) == self.root:
                return False
            with ZipFile(backup_path) as zipobj:
                if "books.json" not in zipobj.namelist():
                    return False
                for name in os.listdir(self.root):
                    path = os.path.join(self.root, name)
                    if os.path.isdir(path):
                        if not (save_thumbnails
                                and os.path.basename(path) == ".thumbnails"):
                            shutil.rmtree(path)
                    else:
                        os.unlink(path)
                zipobj.extractall(self.root)
                self.create_files()
                self.config = BooksConfig(self, os.path.join(self.root, "books.json"))
                self.book_paths = self._read_book_paths()
                self.config["autobackupPath"] = oldBackupPath
                self.config.save()
                return True
        except Exception:
            traceback.print_exc()
            return False

    def resolve_env_variable(self, pattern) -> str:
        matches = re.finditer(VARIABLE_PATTERN, pattern)
        for match in matches:
            value = self.get_var(match.group(1))
            if value:
                pattern = pattern.replace(match.group(), value)
        return pattern

    def resolve_env_path(self, pattern) -> str:
        matches = re.finditer(VARIABLE_PATTERN, pattern)
        paths = []
        for match in matches:
            value = self.get_var(match.group(1))
            if isinstance(value, tuple):
                paths = value
                pattern = pattern.replace(match.group(), "${{...}}")
            elif value:
                pattern = pattern.replace(match.group(), value)
        if paths:
            for path in paths:
                tmp = pattern.replace("${{...}}", path)
                if os.path.exists(tmp):
                    return tmp
        return pattern

    def is_ambiguous_pattern(self, pattern):
        flag = False
        matches = re.finditer(VARIABLE_PATTERN, pattern)
        for match in matches:
            value = self.get_var(match.group(1))
            flag |= isinstance(value, tuple)
        return flag

    def to_book_path(self, path) -> str:
        for bookpath in self.book_paths:
            bookpath = os.path.abspath(bookpath)
            if commonpath([bookpath, os.path.abspath(path)]) == bookpath:
                return os.path.abspath(path).replace(bookpath, "$BOOKS_PATH")
        return os.path.abspath(path)

    def get_var(self, var) -> Union[str, Tuple[str]]:
        if var == "DEFAULT_THUMBNAIL_PATH":
            return self.thumbnail_dir
        elif var == "DEFAULT_USER_THUMBNAIL_PATH":
            return self.user_thumbnail_dir
        elif var == "BOOKS_PATH":
            return tuple(self.book_paths)
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
