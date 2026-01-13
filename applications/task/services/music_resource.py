import requests
import base64
import re

from applications.task.services.acoust import AcoustidClient
from applications.task.services.kugou import KugouClient
from applications.task.services.kuwo import KuwoClient
from applications.task.services.qm import QQMusicApi
from applications.task.services.smart_tag_resource import SmartTagClient
from applications.task.utils import timestamp_to_dt
from applications.utils.send import send


class MusicResource:
    def __init__(self, info):
        self.resource = self.get_resource(info)

    def get_resource(self, info):
        if info == "netease":
            return NetEaseMusicClient()
        elif info == "migu":
            return MiGuMusicClient()
        elif info == "qmusic":
            return QmusicClient()
        elif info == "kugou":
            return KugouClient()
        elif info == "kuwo":
            return KuwoClient()
        elif info == "acoustid":
            return AcoustidClient()
        elif info == "smart_tag":
            return SmartTagClient()
        raise Exception("暂不支持该音乐平台")

    def fetch_lyric(self, song_id):
        try:
            return self.resource.fetch_lyric(song_id)
        except Exception as e:
            print("音乐平台歌词获取失败", e)
            return ""

    def fetch_id3_by_title(self, title):
        try:
            return self.resource.fetch_id3_by_title(title)
        except Exception as e:
            print("音乐平台搜索失败", e)
            return []

    def fetch_album_by_name(self, album_name):
        try:
            if hasattr(self.resource, 'fetch_album_by_name'):
                return self.resource.fetch_album_by_name(album_name)
            return None
        except Exception as e:
            print("音乐平台专辑搜索失败", e)
            return None


class NetEaseMusicClient:
    BASE_URL = "https://music.163.com/"

    def fetch_lyric(self, song_id):
        data = send({"url": self.BASE_URL + "api/song/lyric?lv=-1&kv=-1&tv=-1",
                     "params": {"id": song_id}}, "linuxapi").POST("")
        return data.json().get("lrc", {}).get("lyric")

    def fetch_id3_by_title(self, title):
        data = send({'s': title, 'type': '1', 'limit': '10', 'offset': '0'}).POST("weapi/cloudsearch/get/web")
        try:
            json_data = data.json()
            if json_data.get('code') == 400 or json_data.get('code') == 401:
                # Assuming 400/401 from Netease often means cookie issues or anti-bot
                print("Netease API Error (Cookie?):", json_data)
                raise Exception("Netease Cookie Invalid")
            songs = json_data.get("result", {}).get("songs", [])
        except Exception as e:
            print("网易云音乐搜索失败", e, data.text)
            if "Cookie Invalid" in str(e):
                raise e # Re-raise to be caught by task
            songs = []
        for song in songs:
            artists = song.get("ar", [])
            album = song.get("al", {})
            if artists:
                artist = ",".join([artist.get("name", "") for artist in artists])
                artist_id = artists[0].get("id", "")
            else:
                artist = ""
                artist_id = ""
            year = song.get("publishTime", "")
            if year:
                year = timestamp_to_dt(year / 1000, "%Y")
            song["artist"] = artist
            song["artist_id"] = artist_id
            song["album"] = album.get("name", "")
            song["album_id"] = album.get("id", "")
            song["album_img"] = album.get("picUrl", {})
            song["year"] = year or ""
            song["year"] = year or ""
            # Clean title: remove leading numbers like "01. ", "01 ", "01-"
            song["name"] = re.sub(r'^\d+[\s\.\-]+', '', song.get("name", ""))
            song["source"] = "netease"
        return songs

    def fetch_album_by_name(self, album_name):
        # type=10 means Album search
        data = send({'s': album_name, 'type': '10', 'limit': '5', 'offset': '0'}).POST("weapi/cloudsearch/get/web")
        try:
            albums = data.json().get("result", {}).get("albums", [])
        except Exception as e:
            print("网易云音乐专辑搜索失败", e, data.text)
            return None
        
        if not albums:
            return None
            
        # Use the first match or best match? For now, first match.
        target_album = albums[0]
        album_id = target_album.get("id")
        
        # Now fetch the album details (tracks)
        # Using the standard album details API
        data = send({"url": self.BASE_URL + f"api/v1/album/{album_id}", "params": {}}, "linuxapi").POST("")
        try:
            album_data = data.json()
            songs = album_data.get("songs", [])
            album_info = album_data.get("album", {})
        except Exception as e:
            print("网易云音乐专辑详情获取失败", e)
            return None

        # Process songs into the standard format
        processed_songs = []
        for song in songs:
            artists = song.get("artists") or song.get("ar", [])
            album_obj = song.get("album", {})
            if artists:
                artist = ",".join([artist.get("name", "") for artist in artists])
            else:
                artist = ""
                
            # Netease album detail API returns publishTime in album object usually
            year = album_info.get("publishTime", "")
            if year:
                year = timestamp_to_dt(year / 1000, "%Y")
            
            # Handle both 'name' and 'n' keys (Netease API variations)
            song_name = song.get("name") or song.get("n") or ""
            song_name = re.sub(r'^\d+[\s\.\-]+', '', song_name)  # Clean leading numbers

            processed_songs.append({
                "id": song.get("id"),
                "name": song_name,
                "artist": artist,
                "album": album_info.get("name", ""),
                "album_id": album_info.get("id", ""),
                "album_img": album_info.get("picUrl", ""),
                "year": year or "",
                "duration": song.get("duration") or song.get("dt", 0),  # Duration in ms
                "idx": song.get("no", 0)  # Track number
            })
            
        return {
            "album_name": album_info.get("name", ""),
            "album_artist": ",".join([ar.get("name","") for ar in album_info.get("artists",[])]),
            "album_id": album_info.get("id", ""),
            "album_img": album_info.get("picUrl", ""),
            "year": timestamp_to_dt(album_info.get("publishTime", 0) / 1000, "%Y") if album_info.get("publishTime") else "",
            "tracks": processed_songs
        }

    def search_albums(self, album_name):
        """搜索专辑列表，不获取详细曲目"""
        data = send({'s': album_name, 'type': '10', 'limit': '10', 'offset': '0'}).POST("weapi/cloudsearch/get/web")
        try:
            albums = data.json().get("result", {}).get("albums", [])
        except Exception as e:
            print("网易云音乐专辑搜索失败", e, data.text)
            return []
        
        result = []
        for album in albums:
            artists = album.get("artists", [])
            artist_name = ",".join([ar.get("name", "") for ar in artists]) if artists else ""
            year = album.get("publishTime", "")
            if year:
                year = timestamp_to_dt(year / 1000, "%Y")
            result.append({
                "id": album.get("id"),
                "name": album.get("name", ""),
                "artist": artist_name,
                "cover": album.get("picUrl", ""),
                "year": year or "",
                "size": album.get("size", 0)  # Track count
            })
        return result

    def fetch_album_by_id(self, album_id):
        """通过专辑ID获取专辑详情和曲目"""
        data = send({"url": self.BASE_URL + f"api/v1/album/{album_id}", "params": {}}, "linuxapi").POST("")
        try:
            album_data = data.json()
            songs = album_data.get("songs", [])
            album_info = album_data.get("album", {})
        except Exception as e:
            print("网易云音乐专辑详情获取失败", e)
            return None

        processed_songs = []
        for song in songs:
            artists = song.get("artists") or song.get("ar", [])
            if artists:
                artist = ",".join([artist.get("name", "") for artist in artists])
            else:
                artist = ""
                
            year = album_info.get("publishTime", "")
            if year:
                year = timestamp_to_dt(year / 1000, "%Y")
                
            processed_songs.append({
                "id": song.get("id"),
                "name": re.sub(r'^\d+[\s\.\-]+', '', song.get("name", "")),
                "artist": artist,
                "album": album_info.get("name", ""),
                "album_id": album_info.get("id", ""),
                "album_img": album_info.get("picUrl", ""),
                "year": year or "",
                "duration": song.get("duration", 0),
                "idx": song.get("no", 0)
            })
            
        return {
            "album_name": album_info.get("name", ""),
            "album_artist": ",".join([ar.get("name","") for ar in album_info.get("artists",[])]),
            "album_id": album_info.get("id", ""),
            "album_img": album_info.get("picUrl", ""),
            "year": timestamp_to_dt(album_info.get("publishTime", 0) / 1000, "%Y") if album_info.get("publishTime") else "",
            "tracks": processed_songs
        }


class MiGuMusicClient:
    BASE_URL = "https://m.music.migu.cn/"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
        'Referer': 'https://m.music.migu.cn/'
    }

    def fetch_lyric(self, song_id):
        url = f'https://music.migu.cn/v3/api/music/audioPlayer/getLyric?copyrightId={song_id}'
        res = requests.get(url, headers=self.header)
        return res.json()["lyric"]

    def fetch_id3_by_title(self, title):
        url = self.BASE_URL + f"migu/remoting/scr_search_tag?rows=10&type=2&keyword={title}&pgc=1"
        res = requests.get(url, headers=self.header)
        songs = res.json()["musics"]
        for song in songs:
            song["id"] = song['copyrightId']
            song["name"] = song['songName']
            song["artist"] = song['singerName']
            song["artist_id"] = song['singerId']
            song["album"] = song['albumName']
            song["album_id"] = song['albumId']
            song["album_img"] = song['cover']
            song["year"] = ""
            song["year"] = ""
            song["source"] = "migu"
        return songs


class QmusicClient:
    QQMUSIC_ALBUM_COVER = "http://y.qq.com/music/photo_new/T002R300x300M000{id}.jpg"

    def fetch_lyric(self, song_id):
        a = QQMusicApi()
        res = a.getQQMusicMediaLyric(song_id)
        decoded_str = base64.b64decode(res.get("lyric", "")).decode("utf-8")
        return decoded_str

    def fetch_id3_by_title(self, title):
        a = QQMusicApi()
        songs = a.getQQMusicMatchSong(title)
        for song in songs:
            song["source"] = "qmusic"
        return songs

    def fetch_album_by_name(self, album_name):
        """Search for album by name and return first match with tracks"""
        albums = self.search_albums(album_name)
        if not albums:
            return None
        # Use the first match
        first_album = albums[0]
        album_id = first_album.get("id")
        if not album_id:
            return None
        return self.fetch_album_by_id(album_id)


    def search_albums(self, album_name):
        """搜索专辑列表"""
        import requests
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        data = {
            "comm": {
                "ct": 19, "cv": 1845
            },
            "music.search.SearchCgiService": {
                "method": "DoSearchForQQMusicDesktop",
                "module": "music.search.SearchCgiService",
                "param": {
                    "query": album_name,
                    "num_per_page": 10,
                    "page_num": 1,
                    "search_type": 2  # 2 = album search
                }
            }
        }
        try:
            res = requests.post(url, json=data, headers={
                "referer": "https://y.qq.com/portal/profile.html",
                "Content-Type": "application/json;charset=utf-8"
            })
            result = res.json().get("music.search.SearchCgiService", {}).get("data", {}).get("body", {}).get("album", {}).get("list", [])
        except Exception as e:
            print("QQ音乐专辑搜索失败", e)
            return []

        albums = []
        for album in result:
            singers = album.get("singer_list", [])
            artist = ",".join([s.get("name", "") for s in singers]) if singers else ""
            albums.append({
                "id": album.get("albumMID", ""),
                "name": album.get("albumName", ""),
                "artist": artist,
                "cover": self.QQMUSIC_ALBUM_COVER.format(id=album.get("albumMID", "")),
                "year": album.get("publicTime", "")[:4] if album.get("publicTime") else "",
                "size": album.get("song_count", 0)
            })
        return albums

    def fetch_album_by_id(self, album_id):
        """通过专辑ID获取专辑详情和曲目"""
        import requests
        url = f"https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid={album_id}&format=json&inCharset=utf8&outCharset=utf-8"
        try:
            res = requests.get(url, headers={"referer": "https://y.qq.com/"})
            data = res.json().get("data", {})
        except Exception as e:
            print("QQ音乐专辑详情获取失败", e)
            return None

        album_info = data
        songs = data.get("list", [])

        processed_songs = []
        for song in songs:
            singers = song.get("singer", [])
            artist = ",".join([s.get("name", "") for s in singers]) if singers else ""
            processed_songs.append({
                "id": song.get("songmid", ""),
                "name": re.sub(r'^\d+[\s\.\-]+', '', song.get("songname", "")),
                "artist": artist,
                "album": album_info.get("name", ""),
                "album_id": album_id,
                "album_img": self.QQMUSIC_ALBUM_COVER.format(id=album_id),
                "year": album_info.get("aDate", "")[:4] if album_info.get("aDate") else "",
                "duration": song.get("interval", 0) * 1000,
                "idx": song.get("index", 0)
            })

        return {
            "album_name": album_info.get("name", ""),
            "album_artist": ",".join([s.get("name", "") for s in album_info.get("singer_list", [])]) if album_info.get("singer_list") else "",
            "album_id": album_id,
            "album_img": self.QQMUSIC_ALBUM_COVER.format(id=album_id),
            "year": album_info.get("aDate", "")[:4] if album_info.get("aDate") else "",
            "tracks": processed_songs
        }
