import logging

import urllib.request
from feeluown.utils import aio
from feeluown.gui.helpers import async_run

from .tagger import set_tag_obj

logger = logging.getLogger(__name__)


class TaggerManager:
    def __init__(self):
        self._tagger_map = dict()

    def put_f(self, filename, file_path, tag_obj, cover_url):
        if filename not in self._tagger_map.keys():
            self._tagger_map[filename] = (file_path, tag_obj, cover_url)

    async def set_tag(self, file_path, tag_obj, cover_url):
        cover_data = await async_run(lambda: urllib.request.urlopen(cover_url))
        set_tag_obj(file_path, tag_obj, cover_data)

    def write_tag(self, filename, succeed):
        tag_info = self._tagger_map.pop(filename, None)
        if succeed and tag_info:
            file_path, tag_obj, cover_url = tag_info
            aio.run_afn(self.set_tag, file_path, tag_obj, cover_url)
