import asyncio
import logging
import os

from typing import List

from feeluown.utils import aio
from feeluown.utils.dispatch import Signal
from feeluown.consts import SONG_DIR as DEFAULT_DOWNLOAD_DIR
from feeluown.media import Media

from .downloader import Downloader, AioRequestsDownloader, DownloadTask, DownloadStatus

logger = logging.getLogger(__name__)


class DownloadManager:
    def __init__(self, app, config):
        """

        :type app: feeluown.app.App
        """
        self._app = app
        self._tasks = []
        self._task_queue = asyncio.Queue()

        #: emit List[DownloadTask]
        self.tasks_changed = Signal()
        self.download_finished = Signal()
        self.downloader: Downloader = AioRequestsDownloader()

        self._path = config.DOWNLOAD_DIR or DEFAULT_DOWNLOAD_DIR

    def initialize(self):
        aio.create_task(self.worker())

    def list_tasks(self) -> List[DownloadTask]:
        return self._tasks

    async def get_media(self, media, filename):
        # check if there exists same task
        for task in self.list_tasks():
            if task.filename == filename:
                logger.warning(f'task: {filename} has already been put into queue')
                return

        filepath = self._getpath(filename)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        task = DownloadTask(media, filename, self.downloader)
        self._tasks.append(task)
        await self._task_queue.put(task)
        self.tasks_changed.emit(self.list_tasks())
        logger.info(f'task: {filename} has been put into queue')
        return filepath

    async def get(self, url, filename):
        """download and save a file

        :param url: file url
        :param filename: target file name
        """
        await self.get_media(Media(url), filename)

    async def worker(self):
        while True:
            task = await self._task_queue.get()
            await self.run_task(task)

            # task done and remove task
            self._task_queue.task_done()
            self._tasks.remove(task)
            self.tasks_changed.emit(self.list_tasks())

    async def run_task(self, task: DownloadTask):
        task.status = DownloadStatus.running
        filename = task.filename
        downloader = task.downloader

        filepath = self._getpath(filename)
        try:
            ok = await downloader.run(task.media, filepath)
        except asyncio.CancelledError:
            task.status = DownloadStatus.failed
        except Exception:
            logger.exception('download failed')
            task.status = DownloadStatus.failed
        else:
            if ok:
                task.status = DownloadStatus.ok
            else:
                task.status = DownloadStatus.failed

        # clean up the temp file if needed
        if task.status is DownloadStatus.failed:
            downloader.clean(filepath)
            self.download_finished.emit(filename, False)
            logger.info(f'download content into {filename} failed')
        else:
            path = self._getpath(task.filename)
            logger.info(f'content has been saved into {path}')

    def is_file_downloaded(self, filename):
        return os.path.exists(self._getpath(filename))

    def _getpath(self, filename):
        return os.path.join(self._path, filename)
