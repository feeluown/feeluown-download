"""
fuo_dl
------
fuo_dl 是 FeelUOwn 的一个音乐下载插件。

fuo_dl 支持多首歌并行下载，也支持一首歌分多段并行下载（也就是常说的多线程下载）。
另外，用户可以在 ~/.fuorc 中自定义下载路径::

   config.DOWNLOAD_DIR = '~/Music'
"""

import logging
import os
from concurrent.futures import wait

from .downloader import Downloader
from .progress import ConsoleProgress
from .tagger import Tagger

__alias__ = '音乐下载'
__desc__ = __doc__
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


def download(url, filename, console=False):
    dler = Downloader()
    progress_cb = None
    if console is True:
        progress_cb = ConsoleProgress().on_update
    return dler.create_task(url, filename, progress_cb=progress_cb)


def prepare_url(song, app):
    if song.meta.support_multi_quality:
        media, _ = song.select_media(app.config.AUDIO_SELECT_POLICY)
        url = media.url
        ext = media.metadata.format
    else:
        url = song.url
        ext = url.split('?')[0].split('.')[-1] if '?' in url else 'mp3'

    if not url:
        songs = app.library.list_song_standby(song)
        if songs:
            song = songs[0]
        logger.warning('url source turns to {}: {}-{}-{}-{}'.format(
            song.source, song.title, song.artists_name, song.album_name, song.duration_ms))
        url, ext = prepare_url(song)

    return url, ext


def _generate_tag_obj(song):
    tag_obj = {
        'title': song.title,
        'artist': song.artists_name
    }
    if song.album_name.strip():
        tag_obj['album'] = song.album_name
        tag_obj['albumartist'] = song.album.artists_name
        tag_obj['cover_url'] = song.album.cover

        if hasattr(song.album, '_more_info'):
            album_info = song.album._more_info()
            tag_obj['discnumber'] = album_info.pop('discs')[int(song.identifier)]
            tag_obj['tracknumber'] = album_info.pop('tracks')[int(song.identifier)]
            tag_obj = dict(tag_obj, **album_info)
    else:
        tag_obj['cover_url'] = song.artists[0].cover

    return tag_obj


def _generate_file_path(tag_obj, ext):
    def _check(str):
        return str.replace('/', '_').replace(':', '_')

    SONG_DIR = '~/Music'
    if tag_obj.get('album'):
        storage_path = '{}/{}/{}'.format(SONG_DIR, _check(tag_obj['albumartist']), _check(tag_obj['album']))
        extra_name = ''
        if tag_obj.get('discnumber') and tag_obj.get('tracknumber'):
            extra_name = '{:0>2d} '.format(int(tag_obj['tracknumber'].split('/')[0]))
            if len(tag_obj['discnumber'].split('/')) > 1 and int(tag_obj['discnumber'].split('/')[1]) > 1:
                extra_name = '{}-{}'.format(tag_obj['discnumber'].split('/')[0], extra_name)
        filename = '{}{}.{}'.format(extra_name, tag_obj['title'], ext)
    else:
        storage_path = '{}/{}'.format(SONG_DIR, _check(tag_obj['artist']))
        filename = '{}.{}'.format(tag_obj['title'], ext)
    return storage_path, _check(filename)


def prepare_filename(song, ext):
    tag_obj = _generate_tag_obj(song)

    storage_path, filename = _generate_file_path(tag_obj, ext)
    if not os.path.isdir(storage_path):
        os.makedirs(storage_path)
    filepath = '{}/{}'.format(storage_path, filename)
    return filepath, tag_obj


def download_song(url, filename, tag_obj):
    dler = Downloader()
    download_task = dler.create_task(url, filename, progress_cb=None)
    download_task.add_done_callback(lambda _: Tagger(tag_obj).set_tag_obj(filename))
    return download_task


def enable(app):
    pass


def disable(app):
    pass
