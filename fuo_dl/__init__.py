from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

import requests

from .helpers import ContentRange

__alias__ = '音乐下载'
__desc__ = '音乐下载插件'
__version__ = '0.1'


logger = logging.getLogger(__name__)


def cook_filepath(song):
    """使用非常简陋的方法拼出歌曲的保存路径

    目前的方法有一些问题，一方面没有保证文件后缀正确性，
    另一方面，文件保存路径的计算规则可以有其它一些方法，
    比如按照 `目录/歌手/专辑/歌曲` 这样的形式来存储，
    这个应该给用户提供自定义的能力。

    TODO: 解决上面提到的几个问题
    """
    return '{} - {}.mp3'.format(song.title, song.artists_name)



def download(http, url, index, cr):
    content = None
    return index, content


class DispatchTask:
    def __init__(self, http, url):
        self.http = http
        self.url = url
        self.dl_executor = None

    def run(self):
        # XXX: 多大的 chunksize 比较合适？
        chunksize = 1024 * 1024  # 1MB

        http = self.http
        url = self.url
        executor = self.dl_executor

        resp = http.get(url, stream=True, timeout=2)
        length = resp.headers.get('content-length')
        if length is None:
            content = resp.content
        else:
            parts = length / chunksize
            futures = []
            for i in range(0, parts + 1):
                if i == parts:
                    cr = ContentRange('bytes', i * chunksize, length)
                else:
                    cr = ContentRange('bytes', i * chunksize, chunksize * (i + 1))
                future = executor.submit(download, http, url, i, cr)
                futures.append(future)

            parts = {}
            for future in as_completed(futures):
                index, part = future.result()
                parts[index] = part
            parts = sorted(parts)


class Downloader:
    def __init__(self, http=None, max_workers=None):
        self.pool = ThreadPoolExecutor(max_workers=max_workers)
        self.http = http or requests

        #: {url: [(0, 100), (400, 600)]}
        self.progresses = {}

    def download(self, url):
        http = self.http

        content = bytes()
        resp = http.get(url, stream=True, timeout=2)
        total_size = resp.headers.get('content-length')
        if total_size is None:
            content = resp.content
            return content

        total_size = int(total_size)
        bytes_so_far = 0
        for chunk in resp.iter_content(102400):
            content += chunk
            bytes_so_far += len(chunk)
            progress = round(bytes_so_far * 1.0 / total_size * 100)
        return content

    def put(self, url):
        self.pool.submit(download, http, url)


def enable(app):
    pass


def disable(app):
    pass
