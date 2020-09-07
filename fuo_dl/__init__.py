"""
fuo_dl
------
fuo_dl 是 FeelUOwn 的一个音乐下载插件。

fuo_dl 支持多首歌并行下载，也支持一首歌分多段并行下载（也就是常说的多线程下载）。
另外，用户可以在 ~/.fuorc 中自定义下载路径::

   config.DOWNLOAD_DIR = '~/Music'
"""

import logging

from .manager import DownloadManager

__alias__ = '音乐下载'
__desc__ = __doc__
__version__ = '0.1'


logger = logging.getLogger(__name__)


dm_mgr = None
dm_ui = None


def enable(app):
    global dm_mgr, dm_ui

    # initialize download manager
    dm_mgr = dm_mgr or DownloadManager(app)
    dm_mgr.initialize()

    # initialize ui for download manager
    if app.mode & app.GuiMode:
        from .ui import DownloadUi  # noqa

        dm_ui = dm_ui or DownloadUi(dm_mgr, app, app.ui)
        dm_ui.initialize()


def disable(app):
    pass
