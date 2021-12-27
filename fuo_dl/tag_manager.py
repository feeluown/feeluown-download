import logging
import os

import urllib.request
from feeluown.utils import aio

from .tag_helpers import cook_tagobj, beautify_tagobj, cook_filepath
from .tagger import set_tag_obj

logger = logging.getLogger(__name__)


class TagManager:
    def __init__(self, app):
        self._app = app
        self._tagger_map = dict()

        self._proc_lans = None
        self._name_fmts = None

        self.refine_tagobj_func = None

    def update(self, config):
        self._proc_lans = config.CORE_LANGUAGE
        self._name_fmts = config.NAME_FORMATS

    def prepare_tag(self, song):
        tag_obj, cover_url = cook_tagobj(song, self.refine_tagobj_func)
        tag_obj = beautify_tagobj(tag_obj, self._proc_lans)
        return tag_obj, cover_url

    def prepare_filename(self, tag_obj, ext):
        storage_path, filename = cook_filepath(tag_obj, ext, self._name_fmts)
        return os.path.join(storage_path, filename)

    def put_f(self, filename, file_path, tag_obj, cover_url):
        if filename not in self._tagger_map.keys():
            self._tagger_map[filename] = (file_path, tag_obj, cover_url)

    async def set_tag(self, file_path, tag_obj, cover_url):
        fp = await aio.run_fn(urllib.request.urlopen, cover_url)
        set_tag_obj(file_path, tag_obj, fp.read())
        fp.close()

    def write_tag(self, filename, succeed):
        tag_info = self._tagger_map.pop(filename, None)
        if succeed and tag_info:
            file_path, tag_obj, cover_url = tag_info
            aio.run_afn(self.set_tag, file_path, tag_obj, cover_url)
