from fuo_dl.tag_helpers import *
from feeluown.library.provider import DummySongModel, DummyAlbumModel, DummyArtistModel


def test_beautify_tagobj():
    dict_src = dict(title='test（Live） （Explicit）')
    dict_dst = beautify_tagobj(dict_src, 'auto')
    assert dict_dst['title'] == 'test (Live) (Explicit)'


def test_cook_tagobj():
    artist = DummyArtistModel(identifier=1,
                              name='artist_name',
                              cover='cover_url')
    song = DummySongModel(identifier=1,
                          title='title',
                          artists=[artist],
                          duration=0)

    tag_obj, cover_url = cook_tagobj(song)
    assert tag_obj['title'] == 'title'
    assert tag_obj['artist'] == 'artist_name'
    assert cover_url == 'cover_url'


def test_cook_filepath():

    def get_filepath(tag_obj, ext, fmts):
        storage_path, filename = cook_filepath(tag_obj, ext, fmts)
        return os.path.join(storage_path, filename)

    tag_obj1 = {
        'title': 'ti',
        'artist': 'art',
        'album': 'alb',
        'albumartist': 'alb_art',
        'tracknumber': '1/1',
        'discnumber': '1/1',
    }
    assert get_filepath(tag_obj1, 'flac', ['{albumartist}/{album}/{track} {title}']) == 'alb_art/alb/01 ti.flac'
    assert get_filepath(tag_obj1, 'mp3', ['{albumartist}/{album}/{title}']) == 'alb_art/alb/ti.mp3'
    assert get_filepath(tag_obj1, 'mp3', ['{artist}/{title}']) == 'art/ti.mp3'
    assert get_filepath(tag_obj1, 'm4a', ['{title} - {artist}']) == 'ti - art.m4a'

    tag_obj2 = {
        'title': 'ti',
        'artist': 'art',
        'album': 'alb',
        'albumartist': 'alb_art',
        'tracknumber': '2/2',
        'discnumber': '1/2',
    }
    assert get_filepath(tag_obj2, 'flac', ['{albumartist}/{album}/{track}++{title}']) == 'alb_art/alb/1-02++ti.flac'

    tag_obj3 = {
        'title': 'ti',
        'artist': 'art',
        'album': 'alb',
        'albumartist': 'alb_art',
    }
    assert get_filepath(tag_obj3, 'ape', ['{albumartist}/{album}/{track} {title}',
                                          '{artist}/{title}']) == 'art/ti.ape'