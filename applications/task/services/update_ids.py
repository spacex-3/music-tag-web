import base64
import os

from component import music_tag
from mutagen.flac import VCFLACDict
from mutagen.id3 import TXXX, ID3

from applications.task.models import Task
from applications.utils.constant_template import ConstantTemplate
from applications.utils.send import send


def update_music_info(music_id3_info, is_raw_thumbnail=False):
    for each in music_id3_info:
        print(f"DEBUG_UPDATE_INFO: {each}") # Debug print
        f = music_tag.load_file(each["file_full_path"])
        save_music(f, each, is_raw_thumbnail)
        parent_path = os.path.dirname(each["file_full_path"])
        filename = os.path.basename(each["file_full_path"])
        
        # Build detail message listing what was written
        written_fields = []
        if each.get("title"):
            written_fields.append("标题")
        if each.get("artist"):
            written_fields.append("艺术家")
        if each.get("album"):
            written_fields.append("专辑")
        if each.get("albumartist"):
            written_fields.append("专辑艺术家")
        if each.get("lyrics"):
            written_fields.append("歌词")
        if each.get("album_img"):
            written_fields.append("封面")
        if each.get("year"):
            written_fields.append("年份")
        if each.get("genre"):
            written_fields.append("风格")
        if each.get("tracknumber"):
            written_fields.append("音轨号")
        if each.get("discnumber"):
            written_fields.append("碟片号")
        
        source_map = {
            "netease": "网易云音乐",
            "qmusic": "QQ音乐",
            "migu": "咪咕音乐",
            "kugou": "酷狗音乐",
            "kuwo": "酷我音乐",
            "acoustid": "AcoustID",
            "smart_tag": "智能标签"
        }
        source_name = source_map.get(each.get("source"), each.get("source"))
        
        detail_msg = "写入: " + ", ".join(written_fields) if written_fields else ""
        if source_name:
            detail_msg += f", 来源: {source_name}"
        
        Task.objects.update_or_create(full_path=each["file_full_path"], defaults={
            "state": "success",
            "parent_path": parent_path,
            "filename": filename,
            "song_name": each.get("title", ""),
            "artist_name": each.get("artist", ""),
            "detail_msg": detail_msg
        })


def save_music(f, each, is_raw_thumbnail):
    from applications.task.services.music_ids import MusicIDS

    base_filename = ".".join(os.path.basename(f.filename).split(".")[:-1])
    file_ext = os.path.basename(f.filename).split(".")[-1]

    var_dict = MusicIDS(file=f).var_dict()
    if each.get("title", None):
        if "${" in each["title"]:
            f["title"] = ConstantTemplate(each["title"]).resolve_data(var_dict)
        else:
            f["title"] = each["title"]
    if each.get("artist", None) is not None:
        if "${" in each["artist"]:
            artist = ConstantTemplate(each["artist"]).resolve_data(var_dict)
        else:
            artist = each["artist"]
        artists = artist.split(",")
        f.set("artist", artists)
    if each.get("album", None) is not None:
        if "${" in each["album"]:
            f["album"] = ConstantTemplate(each["album"]).resolve_data(var_dict)
        else:
            f["album"] = each["album"]
    if each.get("albumartist", None):
        if "${" in each["albumartist"]:
            f["albumartist"] = ConstantTemplate(each["albumartist"]).resolve_data(var_dict)
        else:
            f["albumartist"] = each["albumartist"]
    if each.get("discnumber", None):
        if "${" in each["discnumber"]:
            f["discnumber"] = ConstantTemplate(each["discnumber"]).resolve_data(var_dict)
        else:
            try:
                f["discnumber"] = int(each["discnumber"].split("/")[0].strip())
            except:
                f["discnumber"] = 0
    if each.get("tracknumber", None):
        if "${" in each["tracknumber"]:
            f["tracknumber"] = ConstantTemplate(each["tracknumber"]).resolve_data(var_dict)
        else:
            try:
                f["tracknumber"] = int(each["tracknumber"].split("/")[0].strip())
            except:
                f["tracknumber"] = 0
    if each.get("genre", None):
        f["genre"] = each["genre"]
    if each.get("year", None):
        f["year"] = each["year"]
    if each.get("lyrics", None):
        f["lyrics"] = each["lyrics"]
        if each.get("is_save_lyrics_file", False):
            lyrics_file_path = f"{os.path.dirname(each['file_full_path'])}/{base_filename}.lrc"
            with open(lyrics_file_path, "w", encoding="utf-8") as f_lyc:
                f_lyc.write(each["lyrics"])
    else:
        if each.get("lyrics") is not None:
            f.remove_tag("lyrics")
        if each.get("is_save_lyrics_file", False):
            lyrics_file_path = f"{os.path.dirname(each['file_full_path'])}/cover-{base_filename}.lrc"
            if not os.path.exists(lyrics_file_path):
                with open(lyrics_file_path, "w", encoding="utf-8") as f_lyc2:
                    f_lyc2.write(f["lyrics"].value)
    if each.get("comment", None):
        f["comment"] = each["comment"]
    if each.get("album_img", None):
        try:
            img_content = None
            if each["album_img"].startswith("http"):
                img_data = send().GET(each["album_img"])
                if img_data.status_code == 200:
                    img_content = img_data.content
            else:
                img_content = base64.b64decode(each["album_img"])
            if img_content:
                f['artwork'] = img_content
                if each.get("is_save_album_cover", False):
                    format_str = f['artwork'].value.format
                    album_cover_path = f"{os.path.dirname(each['file_full_path'])}/cover-{f['album']}.{format_str}"
                    if os.path.exists(album_cover_path):
                        os.remove(album_cover_path)
                    if not os.path.exists(album_cover_path):
                        with open(album_cover_path, "wb") as f_img:
                            f_img.write(img_content)
                if len(img_content) / 1024 / 1024 > 5:
                    f['artwork'] = f['artwork'].first.raw_thumbnail([2048, 2048])
                if is_raw_thumbnail:
                    f['artwork'] = f['artwork'].first.raw_thumbnail([2048, 2048])
        except Exception as e:
            print(e)
            pass
    else:
        if each.get("is_save_album_cover", False):
            format_str = f['artwork'].value.format
            album_cover_path = f"{os.path.dirname(each['file_full_path'])}/cover-{f['album']}.{format_str}"
            if not os.path.exists(album_cover_path):
                with open(album_cover_path, "wb") as f_img:
                    f_img.write(f['artwork'].value.raw)
    if each.get("album_type", None):
        if isinstance(f.mfile.tags, VCFLACDict):
            f.mfile.tags["RELEASETYPE"] = each["album_type"]
        elif isinstance(f.mfile.tags, ID3):
            f.mfile.tags["MusicBrainz Album Type"] = TXXX(encoding=3,
                                                          desc="MusicBrainz Album Type",
                                                          text=each["album_type"])
        else:
            raise Exception("未知的音乐文件类型")
    if each.get("language", None):
        if isinstance(f.mfile.tags, VCFLACDict):
            f.mfile.tags["LANGUAGE"] = each["language"]
        elif isinstance(f.mfile.tags, ID3):
            f.mfile.tags["LANGUAGE"] = TXXX(encoding=3,
                                            desc="LANGUAGE",
                                            text=each["language"])
        else:
            f.mfile.tags["LANGUAGE"] = each["language"]
    f.save()
    # 重命名文件名称
    if each.get("filename", None):
        if "${" in each["filename"]:
            each["filename"] = ConstantTemplate(each["filename"]).resolve_data(var_dict)
        if not each["filename"].endswith(file_ext):
            each["filename"] = f"{each['filename']}.{file_ext}"
        parent_path = os.path.dirname(each["file_full_path"])
        if each["file_full_path"] != f"{parent_path}/{each['filename']}":
            os.rename(each["file_full_path"], f"{parent_path}/{each['filename']}")
