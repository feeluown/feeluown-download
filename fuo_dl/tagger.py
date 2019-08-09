import logging

import urllib.request

import mutagen
from mutagen.flac import FLAC
from mutagen.apev2 import APEv2
from mutagen.mp3 import EasyMP3
from mutagen.easymp4 import EasyMP4

logger = logging.getLogger(__name__)


class Tagger():

    def __init__(self, tag_info):
        self.tag_info = tag_info

    def set_tag_obj(self, f_path):
        if f_path.endswith('.flac'):
            self._set_tag_info_flac(f_path, self.tag_info)
        elif f_path.endswith('.ape'):
            self._set_tag_info_ape(f_path, self.tag_info)
        elif f_path.endswith('.wav'):
            logger.warning('文件 %s 不支持标签信息的写入', f_path.split('/')[-1])
        elif f_path.endswith('.mp3'):
            self._set_tag_info_mp3(f_path, self.tag_info)
        elif f_path.endswith('.m4a'):
            self._set_tag_info_aac(f_path, self.tag_info)

    def _set_tag_info_flac(self, f_path, tag_info):
        if tag_info.get('date'):
            tag_info['date'] = tag_info['date'] + 'Z'
        if tag_info.get('tracknumber'):
            tag_info['tracknumber'], tag_info['tracktotal'] = tag_info['tracknumber'].split('/')
        if tag_info.get('discnumber'):
            tag_info['discnumber'], tag_info['disctotal'] = tag_info['discnumber'].split('/')

        audio = FLAC(f_path)
        audio.delete()
        for key in tag_info.keys():
            if key == 'cover_url':
                albumart = urllib.request.urlopen(tag_info['cover_url'])
                pic = mutagen.flac.Picture()
                pic.mime = 'image/jpeg'
                pic.type = 3
                pic.data = albumart.read()
                audio.clear_pictures()
                audio.add_picture(pic)
                albumart.close()
            else:
                try:
                    import inlp.convert.chinese as cv
                except Exception as e:
                    audio[key] = tag_info[key]
                else:
                    audio[key] = cv.s2t(tag_info[key])
        audio.save()

    def _set_tag_info_ape(self, f_path, tag_info):
        if tag_info.get('date'):
            tag_info['year'] = tag_info['date'] + 'Z'
        if tag_info.get('tracknumber'):
            tag_info['track'] = tag_info.pop('tracknumber')

        audio = APEv2(f_path)
        audio.delete()
        for key in tag_info.keys():
            if not key == 'cover_url':
                try:
                    import inlp.convert.chinese as cv
                except Exception as e:
                    audio[key] = tag_info[key]
                else:
                    audio[key] = cv.s2t(tag_info[key])
        audio.save()

    def _set_tag_info_mp3(self, f_path, tag_info):
        try:
            # 有些歌曲会有APE格式的标签
            audio = APEv2(f_path)
            audio.delete()
        except Exception as e:
            logger.info(e)

        audio = EasyMP3(f_path)
        audio.delete()
        for key in tag_info.keys():
            if not key == 'cover_url':
                audio[key] = tag_info[key]
        audio.save()

        if tag_info.get('cover_url'):
            audio = mutagen.mp3.MP3(f_path)
            albumart = urllib.request.urlopen(tag_info['cover_url'])
            audio['APIC'] = mutagen.id3.APIC(
                encoding=3,  # 3 is for utf-8
                mime='image/jpeg',  # image/jpeg or image/png
                type=3,  # 3 is for the cover image
                desc='',
                data=albumart.read()
            )
            albumart.close()
            audio.save()

    def _set_tag_info_aac(self, f_path, tag_info):
        if tag_info.get('date'):
            tag_info['date'] = tag_info['date'] + 'Z'
        audio = EasyMP4(f_path)
        audio.delete()
        for key in tag_info.keys():
            if not key == 'cover_url':
                try:
                    import inlp.convert.chinese as cv
                except Exception as e:
                    audio[key] = tag_info[key]
                else:
                    audio[key] = cv.s2t(tag_info[key])
        audio.save()

        if tag_info.get('cover_url'):
            audio = mutagen.mp4.MP4(f_path)
            albumart = urllib.request.urlopen(tag_info['cover_url'])
            audio['covr'] = [mutagen.mp4.MP4Cover(
                albumart.read(),
                imageformat=13  # 13 or 14 for png
            )]
            albumart.close()
            audio.save()