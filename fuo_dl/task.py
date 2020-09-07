from enum import Enum

from .base_downloader import Downloader


class DownloadStatus(Enum):
    pending = 'pending'
    running = 'running'
    ok = 'ok'
    failed = 'failed'


class DownloadTask:
    def __init__(self, url, filename, downloader):
        self.url = url
        self.filename = filename

        self.downloader: Downloader = downloader
        #: task status
        self.status: DownloadStatus = DownloadStatus.pending
