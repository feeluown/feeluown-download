import asyncio
import logging
import os
import re
import unicodedata
import uuid
from enum import Enum
from typing import List

from feeluown.app import App
from feeluown.player import Metadata
from feeluown.media import Media, AudioProps
from feeluown.utils.aio import run_fn, run_afn
from feeluown.utils.dispatch import Signal
from feeluown.library import SongModel, fmt_artists_names, MediaNotFound

from fuo_dl.downloader import AioRequestsDownloader
from fuo_dl.helpers import guess_media_url_ext
from fuo_dl.tagger import set_tag_obj

logger = logging.getLogger(__name__)


def s(song):
    return song.title_display


# Copy from django.
# https://stackoverflow.com/a/295466/4302892
def slugify(value):
    """
    Convert spaces or repeated dashes to single dashes.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Also strip leading and trailing whitespace, dashes, and underscores.
    """
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[^\w\s-]", "", value)
    return re.sub(r"[-\s]+", "-", value).strip("-_")


class DownloadManager:
    def __init__(self, app: App):
        self._app = app
        self._path = app.config.dl.DOWNLOAD_DIR
        self.worker = Worker(self._app)
        self.worker.task_finished.connect(self.on_task_finished)

    def initialize(self):
        run_afn(self.worker.run)

    async def download(self, song):
        self._app.show_msg(f"正在获取需要下载的歌曲信息：{s(song)}")
        try:
            media = await run_fn(
                self._app.library.song_prepare_media,
                song,
                self._app.playlist.audio_select_policy,
            )
        except MediaNotFound:
            self._app.show_msg(f"下载‘{s(song)}’失败：没有找到对应的音频")
            return
        n_song = await run_fn(self._app.library.song_upgrade, song)
        filename = await self._get_filename(n_song, media)
        filepath = os.path.join(self._path, filename)
        if os.path.exists(filepath):
            self._app.show_msg(f"文件已经存在：{filepath}")
            return

        task = DownloadTask(n_song, media, filepath)
        self._app.show_msg(f"下载任务已经提交成功：{s(n_song)}")
        await self.worker.enqueue(task)
        logger.info(f"will download song into {filename}, enqueue task: {task.uuid}")

    async def _get_filename(self, song: SongModel, media: Media):
        props: AudioProps = media.props
        bitrate = props.bitrate
        metadata: Metadata = await self._app.playlist._prepare_metadata_for_song(song)
        default_str = "未知"
        title = metadata["title"] or default_str
        artists_name = fmt_artists_names(metadata["artists"]) or default_str
        album_name = metadata["album"] or default_str
        duration_ms = song.duration_ms
        if props.format:
            ext = props.format
        else:
            ext = guess_media_url_ext(media.url)

        filename = (
            f"{slugify(title)}__{slugify(artists_name)}__{slugify(album_name)}"
            f"__{bitrate}kbps__{duration_ms}.{slugify(ext)}"
        )
        return filename

    def on_task_finished(self, task):
        if task.status == DownloadStatus.ok:
            self._app.show_msg(f"下载成功：{task.filepath}")
        else:
            self._app.show_msg(f"下载失败：{s(task.song)}")


class DownloadStatus(Enum):
    pending = "pending"
    running = "running"
    ok = "ok"
    failed = "failed"


class DownloadTask:
    def __init__(self, song, media: Media, filepath):
        self.uuid = str(uuid.uuid4())
        self.song = song
        self.media = media
        self.filepath = filepath
        self.status: DownloadStatus = DownloadStatus.pending


class Worker:
    def __init__(self, app: App):
        self._app = app
        self._tasks = []
        self._task_queue = asyncio.Queue()

        #: emit List[DownloadTask]
        self.tasks_changed = Signal()
        self.task_finished = Signal()
        self.downloader = AioRequestsDownloader()

    async def enqueue(self, task: DownloadTask):
        await self._task_queue.put(task)
        self._tasks.append(task)
        self.tasks_changed.emit(self.list_tasks())

    def list_tasks(self) -> List[DownloadTask]:
        return self._tasks

    async def run(self):
        while True:
            task = await self._task_queue.get()
            await self._run_task(task)

            # task done and remove task
            self._task_queue.task_done()
            self._tasks.remove(task)
            self.tasks_changed.emit(self.list_tasks())

    async def _run_task(self, task: DownloadTask):
        task.status = DownloadStatus.running
        filepath = task.filepath
        downloader = self.downloader
        try:
            ok = await downloader.run(task.media, filepath)
            metadata: Metadata = await self._app.playlist._prepare_metadata_for_song(
                task.song
            )
            await self._write_tag(filepath, metadata)
        except asyncio.CancelledError:
            task.status = DownloadStatus.failed
        except Exception:
            logger.exception("download failed due to error")
            task.status = DownloadStatus.failed
        else:
            if ok:
                task.status = DownloadStatus.ok
            else:
                task.status = DownloadStatus.failed
        # clean up the temp file if needed
        if task.status is DownloadStatus.failed:
            downloader.clean(filepath)
            logger.info(f"task {task.uuid} failed")
        else:
            logger.info(f"task {task.uuid} finished")
        self.task_finished.emit(task)

    async def _write_tag(self, fpath, metadata: Metadata):
        """write metadata into file"""
        artwork = metadata.get("artwork", "")
        if artwork and self._app.has_gui:
            from feeluown.app.gui_app import GuiApp  # noqa

            artwork_uid = metadata.get("uri", artwork)
            assert isinstance(self._app, GuiApp)
            artwork_data = await self._app.img_mgr.get(artwork, artwork_uid)
        else:
            artwork_data = None
        tag_obj = {
            "title": metadata["title"],
            "artist": fmt_artists_names(metadata["artists"]),
            "album": metadata["album"],
            # TODO: set albumartist field, albumartist=album.artists_name
        }
        set_tag_obj(fpath, tag_obj, artwork_data)
