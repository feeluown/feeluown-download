import asyncio
import logging
import os

from typing import List

from fuocore import aio
from fuocore.dispatch import Signal
from feeluown.consts import SONG_DIR
from .task import DownloadTask, DownloadStatus
from .base_downloader import Downloader, CurlDownloader

logger = logging.getLogger(__name__)


class DownloadManager:
    def __init__(self, app):
        """

        :type app: feeluown.app.App
        """
        self._tasks = []
        self._task_queue = asyncio.Queue()

        #: emit List[DownloadTask]
        self.tasks_changed = Signal()
        self.downloader: Downloader = CurlDownloader()

        self._path = SONG_DIR

    def initialize(self):
        aio.create_task(self.worker())

    def list_tasks(self) -> List[DownloadTask]:
        return self._tasks

    async def get(self, url, filename, headers=None, cookies=None):
        """download and save a file

        :param url: file url
        :param filename: target file name
        """
        # check if there exists same task
        for task in self.list_tasks():
            if task.filename == filename:
                logger.warning(f"task:{filename} has already been put into queue")
                return

        task = DownloadTask(url, filename, self.downloader)
        self._tasks.append(task)
        await self._task_queue.put(task)
        self.tasks_changed.emit(self.list_tasks())
        logger.info(f"task:{filename} has been put into queue")

    async def worker(self):
        while True:
            task = await self._task_queue.get()
            await self.run_task(task)

            # task done and remove task
            self._task_queue.task_done()
            self._tasks.remove(task)
            self.tasks_changed.emit(self.list_tasks())

            path = self._getpath(task.filename)
            logger.info(f'content has been saved into {path}')

    async def run_task(self, task):
        task.status = DownloadStatus.running
        filename = task.filename
        downloader = task.downloader

        filepath = self._getpath(filename)
        try:
            ok = await downloader.run(task.url, filepath)
        except asyncio.CancelledError:
            task.status = DownloadStatus.failed
        else:
            if ok:
                task.status = DownloadStatus.ok
            else:
                task.status = DownloadStatus.failed

        # clean up the temp file if needed
        if task.status is DownloadStatus.failed:
            downloader.clean(filepath)

    def is_file_downloaded(self, filename):
        return os.path.exists(self._getpath(filename))

    def _getpath(self, filename):
        return os.path.join(self._path, filename)
