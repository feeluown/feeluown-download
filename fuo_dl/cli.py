from .downloader import Downloader
from .progress import ConsoleProgress


def download(url, filename, console=False):
    dler = Downloader()
    progress_cb = None
    if console is True:
        progress_cb = ConsoleProgress().on_update
    return dler.create_task(url, filename, progress_cb=progress_cb)
