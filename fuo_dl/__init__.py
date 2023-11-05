"""
fuo_dl
------
fuo_dl 是 FeelUOwn 的一个音乐下载插件。

fuo_dl 支持多首歌并行下载，也支持一首歌分多段并行下载（也就是常说的多线程下载）。
另外，用户可以在 ~/.fuorc 中自定义下载路径::

   config.fuo_dl.DOWNLOAD_DIR = '~/Music'
"""

import logging

from feeluown.consts import SONG_DIR as DEFAULT_DOWNLOAD_DIR
from .manager import DownloadManager
from .tag_manager import TagManager

__alias__ = "音乐下载"
__desc__ = __doc__
__version__ = "0.1"


logger = logging.getLogger(__name__)


dm_mgr = None
tg_mgr = None
dm_ui = None

# keep a reference to the UI instance, so that the install will not be deleted.
dm_ui_v2 = None


def init_config(config):
    config.deffield("DOWNLOAD_DIR", type_=str, default=DEFAULT_DOWNLOAD_DIR, desc="")
    # CORE_LANGUAGE: 写入tag的语言类型, auto/ch/tc: 不进行转换/强制转简体中文/强制转繁体中文
    config.deffield("CORE_LANGUAGE", type_=str, default="auto", desc="")
    # NAME_FORMATS: 以关键字段为标识的命名方式(根据优先级排序的列表), 目前仅支持 albumartist/album/artist/title/track五种字段
    # eg. ['{albumartist}/{album}/{track} {title}', '{albumartist}/{album}/{title}', '{artist}/{title}']
    config.deffield("NAME_FORMATS", type_=list, default=[], desc="")

    # V2 的功能预期和之前（V1）一样，V1 的功能比较丰富，但代码层面比较复杂。
    # V2 只会兼容最新的 Model 设计，这样代码会简单很多。
    config.deffield("ENABLE_V2", type_=bool, default=False)


def enable_v2(app):
    global dm_ui_v2

    if app.mode & app.GuiMode:
        from fuo_dl.v2.ui import UI
        ui = UI(app)
        ui.download_mgr.initialize()
        dm_ui_v2 = ui


def enable(app):
    if app.config.dl.ENABLE_V2:
        return enable_v2(app)


    global dm_mgr, dm_ui, tg_mgr

    # initialize download manager
    dm_mgr = dm_mgr or DownloadManager(app, app.config.fuo_dl)
    dm_mgr.initialize()

    # initialize tag manager
    tg_mgr = tg_mgr or TagManager(app, app.config.fuo_dl)
    app.tag_mgr = tg_mgr

    # initialize ui for download manager
    if app.mode & app.GuiMode:
        from .ui import DownloadUi  # noqa

        dm_ui = dm_ui or DownloadUi(dm_mgr, tg_mgr, app, app.ui)
        dm_ui.initialize()


def disable(app):
    pass
