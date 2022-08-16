import os
import subprocess
import platform

SUPPORTED_FORMATS_NAMES = "All formats (*.*);;PDF (*.pdf);;DJVU (*.djvu *.djv);;EPUB (*.epub)" \
                          ";;MOBI (*.mobi *.azw);;FictionBook (*.fb2, " \
                          "*.fb2z, *.zfb2);;CBZ (*.cbz)"
SUPPORTED_IMAGES_NAMES = "Images (*.jpg *.jpeg *.png)"

SUPPORTED_IMAGES = [
    ".jpg", ".jpeg", ".png"
]

SUPPORTED_FORMATS = [
    ".pdf", ".djvu", ".djv", ".epub",
    ".mobi", ".azw", ".fb2", ".fb2z",
    ".zfb2", ".cbz"
]
SUPPORTED_THUMBNAIL_FORMATS = [
    ".pdf", ".djvu", ".djv", ".epub", ".fb2", ".cbz"
]
BACKUP_FORMAT = ".bsfbackup"
BACKUP_FORMAT_NAME = "Bookshelf backup (*.bsfbackup)"


def resolve_path(*args):
    project_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(project_path, *args))


def open_file(filepath: str):
    if platform.system() == 'Windows':
        os.startfile(filepath)
    elif platform.system() == 'Darwin':
        subprocess.call(('open', filepath))
    else:
        subprocess.call(('xdg-open', filepath))
