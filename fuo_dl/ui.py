import logging

from feeluown.utils import aio
from fuocore.models import ModelType
from feeluown.media import Media
from feeluown.gui.helpers import async_run
from feeluown.gui.widgets.statusline import StatusLineItem

from .manager import DownloadManager
from .helpers import cook_filename, guess_media_url_ext
from .statusline import DownloadLabel

from .tag_manager import TagManager


logger = logging.getLogger(__name__)


class DownloadUi:
    def __init__(self, mgr: DownloadManager, tag_mgr: TagManager, app, ui):
        """

        :type app: feeluown.app.App
        :type ui: feeluown.ui.Ui
        """
        self._mgr = mgr
        self._tag_mgr = tag_mgr
        self._app = app
        self._ui = ui
        self.cur_song_dl_btn = ui.pc_panel.download_btn
        self._ui.bottom_panel.status_line.add_item(
            StatusLineItem('download', DownloadLabel(self._app, mgr)))

    def initialize(self):
        logger.info(f'fuo-dl init')
        self._app.player.media_changed.connect(self._on_media_changed, aioqueue=True)

        # bind download btn clicked signal
        try:
            self.cur_song_dl_btn.disconnect()
        except TypeError:  # signal has no slots
            pass
        self.cur_song_dl_btn.clicked.connect(self._download_cur_media)
        self._ui.pc_panel._sub_top_layout.addSpacing(8)
        self._ui.pc_panel._sub_top_layout.addWidget(self._ui.pc_panel.download_btn)
        self._ui.songs_table.about_to_show_menu.connect(self._add_download_action)
        self.cur_song_dl_btn.show()

        self._mgr.download_finished.connect(self._tag_mgr.write_tag)

    def _on_media_changed(self, media):

        async def func(media):
            # FIXME: current media may be unrelated to current song
            song = self._app.playlist.current_song
            if song is None or media is None:
                self.cur_song_dl_btn.setEnabled(False)
                return
            media_url = media.url
            if media_url and not media_url.startswith('http'):
                self.cur_song_dl_btn.setEnabled(False)
                self.cur_song_dl_btn.setChecked(True)
                return

            ext = guess_media_url_ext(media_url)
            # FIXME: netease need AlbumModel and ArtistModel for more infos
            if False:
                song = await aio.run_fn(self._app.library.song_upgrade, song)
                tag_obj, cover_url = await aio.run_fn(self._tag_mgr.prepare_tag, song)
                filename = self._tag_mgr.prepare_filename(tag_obj, ext)
            else:
                title = await async_run(lambda: song.title)
                artists_name = await async_run(lambda: song.artists_name)
                filename = cook_filename(title, artists_name, ext)
            is_downloaded = self._mgr.is_file_downloaded(filename)
            if is_downloaded:
                self.cur_song_dl_btn.setEnabled(False)
                self.cur_song_dl_btn.setChecked(True)
            else:
                self.cur_song_dl_btn.setEnabled(True)
                self.cur_song_dl_btn.setChecked(False)

        aio.create_task(func(media))

    def _download_cur_media(self):

        song = self._app.playlist.current_song
        if song is None:
            return
        aio.create_task(self.download_song(song))

    async def download_song(self, song):
        media = await aio.run_fn(
            self._app.library.song_prepare_media,
            song,
            self._app.playlist.audio_select_policy)
        media = Media(media)
        media_url = media.url
        if media_url:
            if not media_url.startswith('http'):
                # media_url in local provider is filelname
                logger.info(f'download {media_url} has exists')
                return

            ext = guess_media_url_ext(media_url)
            if self._tag_mgr._name_fmts:
                # FIXME: netease need AlbumModel and ArtistModel for more infos
                song = await aio.run_fn(self._app.library.song_upgrade, song)
                tag_obj, cover_url = await aio.run_fn(self._tag_mgr.prepare_tag, song)
                filename = self._tag_mgr.prepare_filename(tag_obj, ext)
            else:
                title = await async_run(lambda: song.title)
                artists_name = await async_run(lambda: song.artists_name)
                filename = cook_filename(title, artists_name, ext)
            if self._mgr.is_file_downloaded(filename):
                logger.info(f'download {filename} has exists')
                return

            logger.info(f'download {media_url} into {filename}')
            file_path = await self._mgr.get(media_url, filename)
            if self._tag_mgr._name_fmts and file_path:
                self._tag_mgr.put_f(filename, file_path, tag_obj, cover_url)
        else:
            # this should not happen, so we log a error msg
            logger.error('url of current song is empty, will not download')

    def _add_download_action(self, ctx):
        def download(models):
            for model in models:
                if model.meta.model_type == ModelType.song:
                    logger.info(f'add download task: {model}')
                    aio.create_task(self.download_song(model))

        add_action = ctx['add_action']
        add_action('下载歌曲', download)
