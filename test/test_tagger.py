from fuo_dl.tagger import *


def test_set_tag_obj():
    f_path = '08 生之響往.m4a'
    audio = EasyMP4(f_path)
    audio.delete()
    audio.save()

    tag_obj = {
        'title': '生之響往',
        'artist': '刺猬樂隊',
        'album': '生之響往',
        'albumartist': '刺猬樂隊',
        'tracknumber': '8/11',
        'discnumber': '1/1',
        'date': '2018-04-25T07:00:00Z',
        'genre': 'Rock & Roll'
    }
    set_tag_obj(f_path, tag_obj)

    audio = EasyMP4(f_path)
    assert audio['title'] == ['生之響往']
    audio.delete()
    audio.save()
