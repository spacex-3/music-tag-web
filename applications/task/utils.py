# coding:UTF-8
import datetime
import os
import re
import time

from component import music_tag

from applications.task.services.update_ids import save_music
from component.zhconv.zhconv import convert, issimp


def timestamp_to_dt(timestamp, format_type="%Y-%m-%d %H:%M:%S"):
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime(format_type, time_local)
    return dt


def folder_update_time(folder_name):
    stat_info = os.stat(folder_name)
    update_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
    return update_time


def exists_dir(dir_list):
    for _dir in dir_list:
        if os.path.isdir(_dir):
            return True
    return False


def match_score(my_value, u_value):
    try:
        my_value = my_value.lower().replace(" ", "")
        u_value = u_value.lower().replace(" ", "")
        if not issimp(my_value):
            my_value = convert(my_value, 'zh-cn')
        if not issimp(u_value):
            u_value = convert(u_value, 'zh-cn')
        if not my_value or not u_value:
            return 0
        if my_value == u_value:
            return 2
        elif my_value in u_value or u_value in my_value:
            return 1
        return 0
    except Exception:
        return 0


def match_artist(my_value, u_value):
    if "," in u_value:
        return match_score(my_value, u_value.split(",")[0].replace(" ", "")) \
               + match_score(my_value, u_value.split(",")[1].replace(" ", ""))
    else:
        return match_score(my_value, u_value)


def match_song(resource, song_path, select_mode, overwrite_policy="overwrite_all"):
    from applications.task.services.music_resource import MusicResource

    file = music_tag.load_file(song_path)
    file_name = song_path.split("/")[-1]
    file_title = file_name.split('.')[0]
    title = file["title"].value or file_title
    artist = file["artist"].value or ""
    album = file["album"].value or ""

    songs = MusicResource(resource).fetch_id3_by_title(title)

    is_match = False
    song_select = None
    match_score_map = {
        "title": 0,
        "artist": 0,
        "album": 0,
    }
    for song in songs:
        match_score_map["title"] = match_score(title, song["name"])
        match_score_map["artist"] = match_artist(artist if artist else title, song["artist"])
        match_score_map["album"] = match_score(album if album else title, song["album"])
        if artist and match_score_map["artist"] == 0:
            match_score_map["artist"] = -2
        # 标题包含艺术家信息
        if not artist and match_score_map["artist"] >= 1:
            if match_score_map["title"] >= 1:
                match_score_map["title"] = 2
        if sum(match_score_map.values()) >= 3:
            is_match = True
            song_select = song
            break
        if select_mode == "simple":
            if match_score_map["title"] == 2:
                is_match = True
                song_select = song
                break
    if is_match:
        print(f"{title}>>>{song_select['name']}::{match_score_map}")
        song_select["filename"] = file_name
        song_select["file_full_path"] = song_path
        song_select["lyrics"] = MusicResource(resource).fetch_lyric(song_select["id"])
        
        if overwrite_policy == 'overwrite_missing':
            try:
                if file['title'].value: song_select.pop('name', None)
                if file['artist'].value: song_select.pop('artist', None)
                if file['album'].value: song_select.pop('album', None)
                if file['artwork'].value: song_select.pop('album_img', None)
            except Exception as e:
                print(f"Overwrite check error: {e}")

        save_music(file, song_select, False)
    return is_match


def match_album_song(resource, song_path, album_tracks):
    """
    Match a local song file to a track in the album list.
    Matching rules:
    1. Track number (if available)
    2. Title fuzzy match
    """
    from applications.task.services.music_resource import MusicResource
    
    file = music_tag.load_file(song_path)
    file_name = song_path.split("/")[-1]
    file_title = file_name.split('.')[0]
    title = file["title"].value or file_title
    track_num = file["tracknumber"].value
    
    # Try to parse track number from filename if tag is missing
    # e.g. "01. Song.mp3" or "01 - Song.mp3"
    if not track_num:
        match = re.search(r'^(\d+)[\.\s\-]', file_name)
        if match:
            track_num = int(match.group(1))

    is_match = False
    song_select = None
    
    # 1. Try Track Number Match (Strongest Signal)
    if track_num:
        try:
            track_num_int = int(str(track_num).split('/')[0])
            for song in album_tracks:
                song_name = song.get('name') or song.get('songname') or ''
                if song.get('idx') == track_num_int or song.get('track_num') == track_num_int:
                    # Verify with title to avoid complete mismatches
                    if match_score(title, song_name) >= 1: 
                        is_match = True
                        song_select = song
                        print(f"Track Num Match: {title} -> {song_name}")
                        break
        except Exception:
            pass
            
    # 2. Try Title Fuzzy Match (Fallback)
    if not is_match:
        best_score = 0
        for song in album_tracks:
            song_name = song.get('name') or song.get('songname') or ''
            score = match_score(title, song_name)
            if score > best_score:
                best_score = score
                song_select = song
        
        if best_score >= 1: # Require at least partial match
            is_match = True
            song_name = song_select.get('name') or song_select.get('songname') or ''
            print(f"Title Match: {title} -> {song_name}")

    if is_match:
        song_select["filename"] = file_name
        song_select["file_full_path"] = song_path
        # Use existing lyrics fetch logic
        song_select["lyrics"] = MusicResource(resource).fetch_lyric(song_select["id"])
        # Important: Don't save yet, just return the matched data. 
        # The caller will apply album metadata overlay.
        return song_select
        
    return None


def detect_language(lyrics):
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
    english_pattern = re.compile(r'[a-zA-Z]')
    japanese_pattern = re.compile(r'[\u0800-\u4e00]')
    korean_pattern = re.compile(r'[\uac00-\ud7a3]')
    thai_pattern = re.compile(r'[\u0e00-\u0e7f]')

    chinese_count = len(re.findall(chinese_pattern, lyrics))
    english_count = len(re.findall(english_pattern, lyrics))
    japanese_count = len(re.findall(japanese_pattern, lyrics))
    korean_count = len(re.findall(korean_pattern, lyrics))
    thai_count = len(re.findall(thai_pattern, lyrics))
    if chinese_count > english_count and chinese_count > japanese_count and chinese_count > korean_count \
            and chinese_count > thai_count:
        return '中文'
    elif english_count > chinese_count and english_count > japanese_count and english_count > korean_count \
            and english_count > thai_count:
        return '英文'
    elif japanese_count > chinese_count and japanese_count > english_count and japanese_count > korean_count \
            and japanese_count > thai_count:
        return '日文'
    elif korean_count > chinese_count and korean_count > english_count and korean_count > japanese_count \
            and korean_count > thai_count:
        return '韩文'
    elif thai_count > chinese_count and thai_count > english_count and thai_count > japanese_count \
            and thai_count > korean_count:
        return '泰文'
    else:
        return '未知'


def parse_discnumber(discnumber):
    pass


def recursive_scandir(path_list, allow_extensions=None):
    """
    Recursively find all music files in the given list of paths (files or directories).
    """
    if allow_extensions is None:
        from applications.task.constants import ALLOW_TYPE
        allow_extensions = ALLOW_TYPE
    
    music_files = []
    for path in path_list:
        if os.path.isfile(path):
            file_type = path.split(".")[-1].lower()
            if file_type in allow_extensions:
                music_files.append(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    # Ignore hidden files
                    if file.startswith('.'):
                        continue
                        
                    file_type = file.split(".")[-1].lower()
                    if file_type in allow_extensions:
                        music_files.append(os.path.join(root, file))
    
    # Remove duplicates just in case
    return list(set(music_files))
