import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from .helpers import Range


class Downloader:
    def __init__(self, http=None, max_workers=None):
        self.dl_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.dl_range_executor = ThreadPoolExecutor(max_workers=10)
        self.http = http or requests

    def create_task(self, url, filename):
        return self.dl_executor.submit(self._dl, url, filename)

    def _dl(self, url, filename, segment_size=1024*1024*4):
        http = self.http
        executor = self.dl_range_executor

        resp = http.get(url, stream=True, timeout=2)
        length = int(resp.headers.get('content-length'))
        content = bytes()
        if length is None:
            content = resp.content
        else:
            resp.close()
            segment_count = int(length / segment_size)
            if (length % segment_size) != 0:
                segment_count += 1
            futures = []
            for i in range(0, segment_count):
                if i == segment_count - 1:
                    start, end = i * segment_size, length
                else:
                    start, end = i * segment_size, segment_size * (i + 1)
                future = executor.submit(self._dl_range, url, i, start, end)
                futures.append(future)

            segments = []
            for future in as_completed(futures):
                index, segment = future.result()
                segments.append((index, segment))
            segments = sorted(segments, key=lambda part: part[0])
            for _, segment in segments:
                content += segment
        assert len(content) == length
        return content

    def _dl_range(self, url, index, start, end, progress_cb=None):
        t1 = time.time()
        http = self.http
        headers = {'Range': Range('bytes', [(start, end)]).to_header()}
        content = bytes()
        resp = http.get(url, headers=headers, stream=True, timeout=2)
        for chunk in resp.iter_content(1024 * 1024):
            content += chunk
            if progress_cb is not None:
                progress_cb(start, len(content) + start, end)
        return index, content
