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
    """
    Score matching between two strings.
    Returns: 2 = exact match, 1 = substring match, 0 = no match
    Now also checks Chinese-only matching for mixed language filenames.
    """
    try:
        # Normalize: remove all non-alphanumeric chars (keep Chinese), lowercase
        def normalize(s):
            return re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', s).lower()
        
        # Extract Chinese characters only
        def extract_chinese(s):
            return ''.join(re.findall(r'[\u4e00-\u9fa5]+', s))
        
        my_norm = normalize(my_value)
        u_norm = normalize(u_value)
        
        # Also try simplified Chinese conversion
        if not issimp(my_norm):
            my_norm = convert(my_norm, 'zh-cn')
        if not issimp(u_norm):
            u_norm = convert(u_norm, 'zh-cn')
        
        if not my_norm or not u_norm:
            return 0
        
        # Exact normalized match
        if my_norm == u_norm:
            return 2
        
        # Full normalized substring match
        if my_norm in u_norm or u_norm in my_norm:
            return 1
        
        # Chinese-only match (handles "今天没回家 Shanghaied" matching "今天没回家")
        my_chinese = extract_chinese(my_value)
        u_chinese = extract_chinese(u_value)
        if my_chinese and u_chinese:
            if my_chinese == u_chinese:
                return 2
            if my_chinese in u_chinese or u_chinese in my_chinese:
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

        song_select['source'] = resource
        save_music(file, song_select, False)
    return is_match


def match_album_song(resource, song_path, album_tracks):
    """
    Match a local song file to a track in the album list.
    Matching rules:
    1. Song name from FILENAME (priority) - handles multi-disc albums
    2. Track number (fallback for disc 1 ONLY - multi-disc files use name matching only)
    """
    from applications.task.services.music_resource import MusicResource
    
    file = music_tag.load_file(song_path)
    file_name = song_path.split("/")[-1]
    
    # Extract clean song name from FILENAME (not ID3 tag which may be wrong)
    file_title = file_name.rsplit('.', 1)[0]  # Remove extension
    # Remove disc-track prefix like "1-07 " or "2-03 "
    file_title_clean = re.sub(r'^\d+-\d+[\s.\-_]+', '', file_title)
    # Remove simple track prefix like "07 " or "01."
    file_title_clean = re.sub(r'^\d+[\s.\-_]+', '', file_title_clean)
    # Remove any remaining leading digits
    file_title_clean = re.sub(r'^\d+', '', file_title_clean).strip()
    
    # Use cleaned filename for matching (handles multi-disc albums correctly)
    match_title = file_title_clean if file_title_clean else file_title
    
    # Extract disc number and track number from filename
    disc_num = 1  # Default to disc 1
    track_num = None
    # Try disc-track format: "2-07 Song" -> disc=2, track=7
    disc_match = re.match(r'^(\d+)-(\d+)', file_name)
    if disc_match:
        disc_num = int(disc_match.group(1))
        track_num = int(disc_match.group(2))
    else:
        # Try simple format: "07 Song.mp3"
        simple_match = re.match(r'^(\d+)[\s.\-_]', file_name)
        if simple_match:
            track_num = int(simple_match.group(1))

    is_match = False
    song_select = None
    
    # 1. Try Song Name Match FIRST (handles multi-disc albums correctly)
    best_score = 0
    best_song = None
    for song in album_tracks:
        song_name = song.get('name') or song.get('songname') or ''
        score = match_score(match_title, song_name)
        if score > best_score:
            best_score = score
            best_song = song
    
    if best_score >= 1:  # Require at least partial match
        is_match = True
        song_select = best_song
        song_name = song_select.get('name') or song_select.get('songname') or ''
        print(f"Name Match: {file_name} -> {song_name} (score={best_score})")
    
    # 2. Track Number Match (fallback ONLY for disc 1 - multi-disc albums don't work with this)
    # For disc 2+, track number doesn't map to idx correctly, so we skip this
    if not is_match and track_num and disc_num == 1:
        try:
            for song in album_tracks:
                song_name = song.get('name') or song.get('songname') or ''
                if song.get('idx') == track_num or song.get('track_num') == track_num:
                    is_match = True
                    song_select = song
                    print(f"Track Num Match: {file_name} -> {song_name} (track={track_num})")
                    break
        except Exception:
            pass
    
    # Log if no match found for debugging
    if not is_match:
        print(f"NO MATCH: {file_name} (clean_name={match_title}, disc={disc_num}, track={track_num})")

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
