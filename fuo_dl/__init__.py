"""
fuo_dl
------
fuo_dl 是 FeelUOwn 的一个音乐下载插件。

fuo_dl 支持多首歌并行下载，也支持一首歌分多段并行下载（也就是常说的多线程下载）。
另外，用户可以在 ~/.fuorc 中自定义下载路径::

   config.fuo_dl.DOWNLOAD_DIR = '~/Music'
"""

import logging

from .manager import DownloadManager

__alias__ = '音乐下载'
__desc__ = __doc__
__version__ = '0.1'


logger = logging.getLogger(__name__)


dm_mgr = None
dm_ui = None


def init_config(config):
    config.deffield('DOWNLOAD_DIR', type_=str, default=None, desc='')
    # CORE_LANGUAGE: 写入tag的语言类型, auto/ch/tc: 不进行转换/强制转简体中文/强制转繁体中文
    config.deffield('CORE_LANGUAGE', type_=str, default='auto', desc='')
    # NAME_FORMATS: 以关键字段为标识的命名方式(根据优先级排序的列表), 目前仅支持 albumartist/album/artist/title/track五种字段
    # eg. ['{albumartist}/{album}/{track} {title}', '{albumartist}/{album}/{title}', '{artist}/{title}']
    config.deffield('NAME_FORMATS', type_=list, default=None, desc='')


def autoload(app):
    global dm_mgr, dm_ui

    dm_mgr = dm_mgr or DownloadManager(app)
    dm_mgr.update(app.config.fuo_dl)

    if app.mode & app.GuiMode:
        from .ui import DownloadUi  # noqa

        dm_ui = dm_ui or DownloadUi(dm_mgr, app, app.ui)
        dm_ui.update(app.config.fuo_dl)


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

    app.initialized.connect(lambda *args: autoload(*args),
                            weak=False, aioqueue=True)


def disable(app):
    pass
