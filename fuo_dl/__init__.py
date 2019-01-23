"""
fuo_dl
------
fuo_dl 是 FeelUOwn 的一个音乐下载插件。

fuo_dl 支持多首歌并行下载，也支持一首歌分多段并行下载（也就是常说的多线程下载）。
另外，用户可以在 ~/.fuorc 中自定义下载路径::

   config.DOWNLOAD_DIR = '~/Music'
"""



import logging
import sys
import threading
from concurrent.futures import wait

from .downloader import Downloader

__alias__ = '音乐下载'
__desc__ = __doc__
__version__ = '0.1'


logger = logging.getLogger(__name__)


def cook_filepath(song):
    """使用非常简陋的方法拼出歌曲的保存路径

    目前的方法有一些问题，一方面没有保证文件后缀正确性，
    另一方面，文件保存路径的计算规则可以有其它一些方法，
    比如按照 `目录/歌手/专辑/歌曲` 这样的形式来存储，
    这个应该给用户提供自定义的能力。

    TODO: 解决上面提到的几个问题
    """
    return '{} - {}.mp3'.format(song.title, song.artists_name)


class ConsoleProgress:
    def __init__(self, length):
        self.length = length
        self.lock = threading.Lock()
        self.progress = {}

    def update(self, start, current, end):
        with self.lock:
            progress = self.progress
            length = self.length
            progress[(start, end)] = current

            fill = "█"
            not_fill = "-"
            total = 50

            fill_pos = set()
            print('\rProgress: ', end='')
            for r, c in progress.items():
                s, _ = r
                i1 = int(s / length * total)
                i2 = int(c / length * total)
                while i1 < i2:
                    fill_pos.add(i1)
                    i1 += 1
            for num in range(0, total + 1):
                c = fill if num in fill_pos else not_fill
                print(c, end='')
            sys.stdout.flush()

    def dl_callback(self):
        pass

    def dl_range_callback(self):
        pass


def download(url, filename):
    dler = Downloader()
    wait([dler.create_task(url, filename)])


def enable(app):
    pass


def disable(app):
    pass
