import logging

from feeluown.app.gui_app import GuiApp
from feeluown.utils.aio import run_afn
from feeluown.library import ModelType
from feeluown.gui.widgets.statusline import StatusLineItem

from fuo_dl.statusline import DownloadLabel
from .manager import DownloadManager

logger = logging.getLogger(__name__)


class UI:
    """
    Download UI 提供几个功能
    """

    def __init__(self, app: GuiApp):
        self._app = app
        self._ui = app.ui
        self.download_mgr = DownloadManager(self._app)

        self._ui.songs_table.about_to_show_menu.connect(self._add_download_action)
        self._ui.bottom_panel.status_line.add_item(
            StatusLineItem("download",
                           DownloadLabel(self._app, self.download_mgr.worker)))

    def _add_download_action(self, ctx):
        def download(models):
            # Note that these models may be the same.
            for model in set(models):
                if model.meta.model_type == ModelType.song:
                    logger.info(f"add download task: {model}")
                    run_afn(self.download_mgr.download, model)

        add_action = ctx["add_action"]
        add_action("下载歌曲", download)
