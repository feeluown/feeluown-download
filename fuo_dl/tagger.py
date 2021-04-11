import logging

import urllib.request

import mutagen
from mutagen.flac import FLAC
from mutagen.apev2 import APEv2
from mutagen.mp3 import EasyMP3
from mutagen.easymp4 import EasyMP4

logger = logging.getLogger(__name__)


def set_tag_info_flac(f_path, tag_info, cover=None):
    if tag_info.get('date'):
        tag_info['date'] = tag_info['date'] + 'Z'
    if tag_info.get('tracknumber'):
        tag_info['tracknumber'], tag_info['tracktotal'] = tag_info['tracknumber'].split('/')
    if tag_info.get('discnumber'):
        tag_info['discnumber'], tag_info['disctotal'] = tag_info['discnumber'].split('/')

    audio = FLAC(f_path)
    audio.delete()
    for key in tag_info.keys():
        audio[key] = tag_info[key]
    if cover:
        albumart = urllib.request.urlopen(cover)
        pic = mutagen.flac.Picture()
        pic.mime = 'image/jpeg'
        pic.type = 3
        pic.data = albumart.read()
        audio.clear_pictures()
        audio.add_picture(pic)
        albumart.close()
    audio.save()


def set_tag_info_ape(f_path, tag_info, cover=None):
    if tag_info.get('date'):
        tag_info['year'] = tag_info['date'] + 'Z'
    if tag_info.get('tracknumber'):
        tag_info['track'] = tag_info.pop('tracknumber')

    audio = APEv2(f_path)
    audio.delete()
    for key in tag_info.keys():
        audio[key] = tag_info[key]
    audio.save()


def set_tag_info_mp3(f_path, tag_info, cover=None):
    try:
        # 有些歌曲会有APE格式的标签
        audio = APEv2(f_path)
        audio.delete()
    except Exception as e:
        logger.debug(e)

    audio = EasyMP3(f_path)
    audio.delete()
    for key in tag_info.keys():
        audio[key] = tag_info[key]
    audio.save()
    if cover:
        audio = mutagen.mp3.MP3(f_path)
        albumart = urllib.request.urlopen(cover)
        audio['APIC'] = mutagen.id3.APIC(
            encoding=3,  # 3 is for utf-8
            mime='image/jpeg',  # image/jpeg or image/png
            type=3,  # 3 is for the cover image
            desc='',
            data=albumart.read()
        )
        albumart.close()
        audio.save()


def set_tag_info_aac(f_path, tag_info, cover=None):
    if tag_info.get('date'):
        tag_info['date'] = tag_info['date'] + 'Z'

    audio = EasyMP4(f_path)
    audio.delete()
    for key in tag_info.keys():
        audio[key] = tag_info[key]
    audio.save()
    if cover:
        audio = mutagen.mp4.MP4(f_path)
        albumart = urllib.request.urlopen(cover)
        audio['covr'] = [mutagen.mp4.MP4Cover(
            albumart.read(),
            imageformat=13  # 13 or 14 for png
        )]
        albumart.close()
        audio.save()


def set_tag_obj(f_path, tag_info, cover=None):
    # logger.info('"%s": download successfully', f_path.split('/')[-1])

    ext = f_path.split('.')[-1]
    if ext in ['flac', 'ape', 'wav', 'mp3', 'm4a']:
        if f_path.endswith('.wav'):
            logger.warning('"%s": unsupported file', f_path.split('/')[-1])
            return

        if f_path.endswith('.flac'):
            func = set_tag_info_flac
        elif f_path.endswith('.ape'):
            func = set_tag_info_ape
        elif f_path.endswith('.mp3'):
            func = set_tag_info_mp3
        elif f_path.endswith('.m4a'):
            func = set_tag_info_aac
        func(f_path, tag_info, cover)
        # logger.info('"%s": tag successfully', f_path.split('/')[-1])
    else:
        logger.warning('"%s": unknown filetype', f_path.split('/')[-1])
