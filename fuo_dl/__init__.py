"""
fuo_dl
------
fuo_dl 是 FeelUOwn 的一个音乐下载插件。

fuo_dl 支持多首歌并行下载，也支持一首歌分多段并行下载（也就是常说的多线程下载）。
另外，用户可以在 ~/.fuorc 中自定义下载路径::

   config.DOWNLOAD_DIR = '~/Music'
"""



import logging
from concurrent.futures import wait

from .downloader import Downloader
from .progress import ConsoleProgress

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


def download(url, filename, console=False):
    dler = Downloader()
    progress_cb = None
    if console is True:
        progress_cb = ConsoleProgress().on_update
    return dler.create_task(url, filename, progress_cb=progress_cb)


def enable(app):
    pass


def disable(app):
    pass
