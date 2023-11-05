import asyncio
import logging
import os
import uuid
from enum import Enum
from typing import List

from feeluown.app import App
from feeluown.player import Metadata
from feeluown.media import Media, AudioProps
from feeluown.utils.aio import run_fn, run_afn
from feeluown.utils.dispatch import Signal
from feeluown.library import SongModel, fmt_artists_names

from fuo_dl.downloader import AioRequestsDownloader
from fuo_dl.helpers import guess_media_url_ext

logger = logging.getLogger(__name__)


class DownloadManager:
    def __init__(self, app: App):
        self._app = app
        self._path = app.config.dl.DOWNLOAD_DIR
        self.worker = Worker()
        self.worker.task_finished.connect(self.on_task_finished)

    def initialize(self):
        run_afn(self.worker.run)

    async def download(self, song):
        media = await run_fn(
            self._app.library.song_prepare_media,
            song,
            self._app.playlist.audio_select_policy,
        )
        n_song = await run_fn(self._app.library.song_upgrade, song)
        filename = await self._get_filename(n_song, media)
        filepath = os.path.join(self._path, filename)

        task = DownloadTask(n_song, media, filepath)
        self._app.show_msg(f'下载任务已经提交成功：{n_song}')
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
        ext = guess_media_url_ext(media.url)
        filename = (
            f"{title}__{artists_name}__{album_name}__{bitrate}kbps__{duration_ms}.{ext}"
        )
        return filename

    def on_task_finished(self, task):
        if task.status == DownloadStatus.ok:
            self._app.show_msg(f'下载成功：{task.song}，{task.filepath}')
        else:
            self._app.show_msg(f'下载失败：{task.song}')


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
    def __init__(self):
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

    async def _run_task(self, task):
        task.status = DownloadStatus.running
        filepath = task.filepath
        downloader = self.downloader
        try:
            ok = await downloader.run(task.media, filepath)
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
