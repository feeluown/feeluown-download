import logging
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
from .helpers import Range

logger = logging.getLogger(__name__)


class InvalidUrl(Exception):
    pass


def divide(length, segment_size):
    """将一跟线段细分成多段

    """
    segment_count = int(length / segment_size)
    if (length % segment_size) != 0:
        segment_count += 1
    for i in range(0, segment_count):
        if i == segment_count - 1:
            start, end = i * segment_size, length
        else:
            start, end = i * segment_size, segment_size * (i + 1)
        yield (i, start, end)


class FileDownloadTask:
    def __init__(self, url, filename, progress_cb=None):
        self.url = url
        self.filename = filename
        self.seek_write_lock = threading.Lock()

        self.progress_cb = progress_cb

    def run(self, executor, http, segment_size=1024*1024*4):
        self.executor = executor
        self.http = http
        self.segment_size = segment_size

        self._dl()

    def _get_length(self):
        """发送 HEAD 请求，尝试获取文件大小

        如果能获取，则返回长度，否则返回 None，遇到时错误抛出异常。
        """
        resp = self.http.head(self.url, timeout=1)
        status_code = resp.status_code
        if status_code >= 400:
            logger.warning('Get file length failed, status:%d', status_code)
            if status_code == 403:
                logger.warning('It seems that the url:%s is expired', self.url)
            raise InvalidUrl("Head request failed, status:{}".format(status_code))
        if 200 <= status_code < 300:
            length = int(resp.headers.get('content-length'))
            return length

    def _dl(self):
        url = self.url
        executor = self.executor

        length = self._get_length()
        if length is None:
            raise RuntimeError("only support downloading those files with length.")

        with open(self.filename, 'wb') as f:
            futures = []
            for _, start, end in divide(length, self.segment_size):
                futures.append(executor.submit(self._dl_range, f, url, start, end, length))
            for future in futures:
                future.result()  # get each future result to detect exception

    def _dl_range(self, f, url, start, end, length):
        http = self.http
        headers = {'Range': Range('bytes', [(start, end)]).to_header()}
        resp = http.get(url, headers=headers, stream=True, timeout=5)
        size = 0
        for chunk in resp.iter_content(1024 * 8):
            with self.seek_write_lock:
                f.seek(start + size)
                f.write(chunk)
            size += len(chunk)
            if self.progress_cb is not None:
                try:
                    self.progress_cb(start, size + start, end, length)
                except:  # noqa
                    logger.exception('Progress callback failed.')


class Downloader:
    def __init__(self, max_workers=None):
        self.dl_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.dl_range_executor = ThreadPoolExecutor(max_workers=10)

    def create_task(self, url, filename, http=None, progress_cb=None):
        task = FileDownloadTask(url, filename, progress_cb=progress_cb)
        return self.dl_executor.submit(
            task.run, self.dl_range_executor, http or requests)
