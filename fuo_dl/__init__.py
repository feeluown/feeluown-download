from concurrent.futures import ThreadPoolExecutor


__alias__ = '音乐下载'
__desc__ = '音乐下载插件'
__version__ = '0.1'


class Downloader:
    def __init__(self, max_workers=None):
        self.pool = ThreadPoolExecutor(max_workers=max_workers)


def enable(app):
    pass


def disable(app):
    pass
