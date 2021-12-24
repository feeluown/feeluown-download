import logging
import os


logger = logging.getLogger(__name__)


def beautify_tagobj(tag_obj, lans):
    def beautify_str(_str):
        return _str.replace(' （', ' (').replace('（', ' (').replace('）', ')').strip()

    try:
        assert lans in ['auto', 'cn', 'tc']
        if lans in ['cn', 'tc']:
            import inlp.convert.chinese as cv
            def post_proc(_str):
                _str = beautify_str(_str)
                return cv.t2s(_str) if lans == 'cn' else cv.s2t(_str)
        else:
            def post_proc(_str):
                return beautify_str(_str)
    except Exception as e:
        logger.warning(e)
        def post_proc(_str):
            return beautify_str(_str)

    for key in tag_obj.keys():
        tag_obj[key] = post_proc(tag_obj[key])
    return tag_obj


def cook_tagobj(song, extra_func=None):
    tag_obj = {
        'title': song.title,
        'artist': song.artists_name
    }

    if song.album_name.strip():
        tag_obj['album'] = song.album.name
        tag_obj['albumartist'] = song.album.artists_name
        cover_url = song.album.cover
        if extra_func:
            song_info = extra_func(song)
            tag_obj = dict(tag_obj, **song_info)
    else:
        cover_url = song.artists[0].cover
    return tag_obj, cover_url


def cook_filepath_old(tag_obj, ext):
    def correct_str(_str):
        return _str.replace('/', '_').replace(':', '_')

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


def cook_filepath(tag_obj, ext, fmts):
    def correct_str(_str):
        return _str.replace('/', '_').replace(':', '_')

    # 目前支持获取的tag字段和计算方法
    valid_tag_map = dict()
    if tag_obj.get('albumartist'): valid_tag_map['albumartist'] = correct_str(tag_obj['albumartist'])
    if tag_obj.get('album'): valid_tag_map['album'] = correct_str(tag_obj['album'])
    if tag_obj.get('artist'): valid_tag_map['artist'] = correct_str(tag_obj['artist'])
    if tag_obj.get('title'): valid_tag_map['title'] = correct_str(tag_obj['title'])
    if tag_obj.get('discnumber') and tag_obj.get('tracknumber'):
        valid_tag_map['track'] = '{:0>2d}'.format(int(tag_obj['tracknumber'].split('/')[0]))
        if len(tag_obj['discnumber'].split('/')) > 1 and int(tag_obj['discnumber'].split('/')[1]) > 1:
            # 只有在disc的总数>1时, 我们需要对不同disc相同track的歌曲进行区分
            valid_tag_map['track'] = '{}-{}'.format(valid_tag_map['discnumber'].split('/')[0], valid_tag_map['track'])

    # 最坏的情况, 只有'{title}'字段有效
    if '{title}' not in fmts:
        fmts.append('{title}')
    for fmt in fmts:
        try:
            # 确定当前的fmt所需要的所有字段, 判断valid_tag_map中是否全部拥有
            import re
            ks = re.findall(r'{(.*?)}', fmt)
            assert all(k in valid_tag_map.keys() for k in ks)

            # 全部都拥有时进行一一替换
            filename = os.path.join(*(fmt.split('/')))
            for k in set(ks):
                filename = filename.replace(f'{{{k}}}', valid_tag_map[k])

            # 得到路径和文件名
            storage_path = os.path.dirname(filename)
            filename = '{}.{}'.format(os.path.basename(filename), ext)
            return storage_path, filename
        except Exception as e:
            logger.warning(e)
            # 没有全部拥有时, 尝试以相同逻辑处理下一fmt, 直至匹配成功
            continue


def prepare_filename(song, ext, lans, fmts, extra_func=None):
    tag_obj, cover_url = cook_tagobj(song, extra_func)
    tag_obj = beautify_tagobj(tag_obj, lans)

    storage_path, filename = cook_filepath(tag_obj, ext, fmts)
    return os.path.join(storage_path, filename), tag_obj, cover_url
