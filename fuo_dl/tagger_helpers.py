import logging
import os

from feeluown.gui.helpers import async_run

logger = logging.getLogger(__name__)


async def cook_tagobj(song):
    def beautify_str(str):
        return str.replace(' （', ' (').replace('（', ' (').replace('）', ')').strip()

    title = await async_run(lambda: song.title)
    artists_name = await async_run(lambda: song.artists_name)

    tag_obj = {
        'title': title,
        'artist': artists_name
    }

    album_name = await async_run(lambda: song.album_name.strip())
    if album_name:
        tag_obj['album'] = await async_run(lambda: song.album_name)
        tag_obj['albumartist'] = await async_run(lambda: song.album.artists_name)
        cover_url = await async_run(lambda: song.album.cover)

        if hasattr(song.album, '_more_info'):
            album_info = await async_run(lambda: song.album._more_info())
            if int(song.identifier) in album_info['discs']:
                tag_obj['discnumber'] = album_info.pop('discs')[int(song.identifier)]
                tag_obj['tracknumber'] = album_info.pop('tracks')[int(song.identifier)]
            else:
                album_info.pop('discs')
                album_info.pop('tracks')
            tag_obj = dict(tag_obj, **album_info)
    else:
        cover_url = await async_run(lambda: song.artists[0].cover)

    for key in tag_obj.keys():
        try:
            import inlp.convert.chinese as cv
        except Exception as e:
            logger.warning(e)
            tag_obj[key] = beautify_str(tag_obj[key])
        else:
            tag_obj[key] = cv.s2t(beautify_str(tag_obj[key]))
    return tag_obj, cover_url


def cook_filepath(tag_obj, ext):
    def correct_str(str):
        return str.replace('/', '_').replace(':', '_')

    if tag_obj.get('album'):
        storage_path = os.path.join(correct_str(tag_obj['albumartist']), correct_str(tag_obj['album']))
        extra_name = ''
        if tag_obj.get('discnumber') and tag_obj.get('tracknumber'):
            extra_name = '{:0>2d} '.format(int(tag_obj['tracknumber'].split('/')[0]))
            if len(tag_obj['discnumber'].split('/')) > 1 and int(tag_obj['discnumber'].split('/')[1]) > 1:
                extra_name = '{}-{}'.format(tag_obj['discnumber'].split('/')[0], extra_name)
        filename = '{}{}.{}'.format(extra_name, correct_str(tag_obj['title']), ext)
    else:
        storage_path = correct_str(tag_obj['artist'])
        filename = '{}.{}'.format(correct_str(tag_obj['title']), ext)
    return storage_path, filename


async def prepare_filename(song, ext):
    tag_obj, cover_url = await cook_tagobj(song)
    storage_path, filename = cook_filepath(tag_obj, ext)
    return os.path.join(storage_path, filename), tag_obj, cover_url
