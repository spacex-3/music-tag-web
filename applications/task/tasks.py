import datetime
import os
import shutil
import time
import uuid
from collections import defaultdict

from component import music_tag
from django.conf import settings
from django.db import transaction

from applications.music.models import Folder, Track, Album, Genre, Artist, Attachment
from applications.subsonic.constants import AUDIO_EXTENSIONS_AND_MIMETYPE, COVER_TYPE
from applications.task.constants import ALLOW_TYPE
from applications.task.models import TaskRecord, Task
from applications.task.services.music_ids import MusicIDS
from applications.task.services.music_resource import MusicResource
from applications.task.services.scan_utils import ScanMusic, MusicInfo
from applications.task.services.scan_utils import ScanMusic, MusicInfo
from applications.task.utils import folder_update_time, exists_dir, match_song, match_album_song
from applications.task.services.update_ids import save_music
from django_vue_cli.celery_app import app


def get_uuid():
    return str(uuid.uuid4())


@app.task
def full_scan_folder(sub_path=None):
    a = time.time()
    bulk_create = []
    music_folder = os.path.join(settings.MEDIA_ROOT, "music")
    ignore_path = [os.path.join(music_folder, "data")]
    if sub_path:
        stack = sub_path
    else:
        stack = [(None, music_folder)]
    while len(stack) != 0:
        # 从栈里取出数据
        parent_uid, dir_data = stack.pop()
        if os.path.isdir(dir_data):
            if dir_data in ignore_path:
                continue
            try:
                entries = os.scandir(dir_data)
                my_uuid = get_uuid()
            except Exception as e:
                m = f"Error while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            try:
                sub_path = [(my_uuid, entry.path) for entry in entries]
            except Exception as e:
                m = f"Error2 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            finally:
                if hasattr(entries, "close"):
                    entries.close()

            # stack.extend(sub_path)
            if sub_path:
                full_scan_folder.delay(sub_path=sub_path)
            bulk_create.append(
                Folder(**{
                    "name": dir_data.split("/")[-1],
                    "path": dir_data,
                    "file_type": "folder",
                    "uid": my_uuid,
                    "parent_id": parent_uid
                })
            )
        else:
            suffix = dir_data.split(".")[-1]
            if suffix in dict(AUDIO_EXTENSIONS_AND_MIMETYPE):
                my_uuid = get_uuid()
                bulk_create.append(
                    Folder(**{
                        "name": dir_data.split("/")[-1],
                        "path": dir_data,
                        "file_type": "music",
                        "uid": my_uuid,
                        "parent_id": parent_uid
                    })
                )
            elif suffix in COVER_TYPE:
                my_uuid = get_uuid()
                bulk_create.append(
                    Folder(**{
                        "name": dir_data.split("/")[-1],
                        "path": dir_data,
                        "file_type": "image",
                        "uid": my_uuid,
                        "parent_id": parent_uid
                    })
                )
        if len(bulk_create) % 500 == 0:
            Folder.objects.bulk_create(bulk_create, batch_size=500)
            bulk_create = []
    if len(bulk_create) > 0:
        Folder.objects.bulk_create(bulk_create, batch_size=500)
    print("完成扫描！", time.time() - a)


@app.task
def update_scan_folder(sub_path=None):
    music_folder = os.path.join(settings.MEDIA_ROOT, "music")
    ignore_path = [os.path.join(music_folder, "data")]
    print(music_folder)
    if sub_path:
        stack = sub_path
    else:
        stack = [(None, music_folder)]
    last_folder = Folder.objects.order_by("-last_scan_time").first()
    if last_folder:
        last_scan_time = last_folder.last_scan_time
    else:
        last_scan_time = datetime.datetime(1970, 1, 1)
    now_time = datetime.datetime.now()
    while len(stack) != 0:
        # 从栈里取出数据
        parent_uid, dir_data = stack.pop(0)
        if dir_data in ignore_path:
            continue
        if os.path.isdir(dir_data):
            try:
                sub_path = os.scandir(dir_data)
            except Exception as e:
                m = f"Error3 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            update_time = folder_update_time(dir_data)
            if update_time < last_scan_time:
                try:
                    sub_path_list = [i.path for i in sub_path]
                except Exception as e:
                    m = f"Error4 while reading {dir}: {e.__class__.__name__} {e}\n"
                    print(m)
                    continue
                finally:
                    if hasattr(sub_path, "close"):
                        sub_path.close()
                if not exists_dir(sub_path_list):
                    continue
            current_folder = Folder.objects.filter(path=dir_data).first()
            if current_folder:
                my_uuid = current_folder.uid
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "folder",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                }
            else:
                my_uuid = get_uuid()
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "folder",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                }
            Folder.objects.update_or_create(path=dir_data, defaults=update_data)
            try:
                sub_path = [(my_uuid, f"{dir_data}/{i}") for i in sub_path]
            except Exception as e:
                m = f"Error5 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            finally:
                if hasattr(sub_path, "close"):
                    sub_path.close()
            # stack.extend(sub_path)
            if sub_path:
                update_scan_folder.delay(sub_path)
        else:
            suffix = dir_data.split(".")[-1]
            if suffix in dict(AUDIO_EXTENSIONS_AND_MIMETYPE):
                print(dir_data)
                my_uuid = get_uuid()
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "music",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                    "state": "updated"
                }
            elif suffix in COVER_TYPE:
                my_uuid = get_uuid()
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "image",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                    "state": "updated"
                }
            else:
                continue
            Folder.objects.update_or_create(path=dir_data, defaults=update_data)
    folder_lst = Folder.objects.filter(updated_at=now_time, file_type="folder")
    for folder in folder_lst:
        path_list = list(
            Folder.objects.filter(parent_id=folder.uid).exclude(updated_at=now_time).values_list("path", flat=True))
        with transaction.atomic():
            Track.objects.filter(path__in=path_list).delete()
            Folder.objects.filter(parent_id=folder.uid).exclude(updated_at=now_time).delete()

    print("完成更新扫描！")


@app.task
def scan_folder():
    if Folder.objects.count() > 0:
        update_scan_folder()
    else:
        full_scan_folder()


@app.task
def scan_music_id3():
    a = time.time()
    ScanMusic("/").scan()
    print(time.time() - a)


@app.task
def scan():
    if Folder.objects.count() > 0:
        update_scan_folder()
    else:
        full_scan_folder()
    ScanMusic("/").scan()


def clear_music():
    Folder.objects.all().delete()
    Track.objects.all().delete()
    Album.objects.all().delete()
    Genre.objects.all().delete()
    Artist.objects.all().delete()
    Attachment.objects.all().delete()


@app.task(bind=True)
def batch_auto_tag_task(self, batch=None, source_list=None, select_mode=None, overwrite_policy="overwrite_all", skip_scraped=False, folder_path=None):
    """
    自动刮削任务
    source_list: ["migu", "qmusic", "netease"]
    skip_scraped: If True, skip files that are already in Task table (any state)
    folder_path: If provided, scan this folder recursively (used for scheduled scraping)
    """
    logs = []
    success_count = 0
    fail_count = 0
    skip_count = 0
    cookie_warning = False
    failed_items = []
    success_items = []
    skipped_items = []

    def log(msg, type="info"):
        logs.append({"msg": msg, "type": type})
        print(msg)

    # If folder_path is provided (scheduled scraping), scan the folder directly
    if folder_path and os.path.isdir(folder_path):
        log(f"Scheduled scraping: Scanning {folder_path}")
        batch = f"scheduled_{int(time.time())}"  # Generate batch ID
        
        # Recursively find all music files
        bulk_set = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_type = file.split(".")[-1].lower()
                if file_type not in ALLOW_TYPE:
                    continue
                full_path = os.path.join(root, file)
                
                # Skip if already scraped (any state)
                if skip_scraped:
                    existing = Task.objects.filter(full_path=full_path).exists()
                    if existing:
                        log(f"Skipping (already in history): {file}")
                        skip_count += 1
                        Task.objects.update_or_create(full_path=full_path, defaults={
                            "state": "skipped",
                            "parent_path": root,
                            "filename": file,
                            "updated_at": datetime.datetime.now()
                        })
                        skipped_items.append({"name": file, "full_path": full_path})
                        continue
                
                file_name = ".".join(file.split(".")[:-1])
                bulk_set.append(TaskRecord(**{
                    "batch": batch,
                    "song_name": file_name,
                    "full_path": full_path,
                    "icon": "icon-music",
                }))
        
        TaskRecord.objects.bulk_create(bulk_set, batch_size=500)
        log(f"Found {len(bulk_set)} files to process (skipped {skip_count})")
        
    # Normal mode: process pre-created TaskRecord entries
    else:
        # Apply skip_scraped filter to existing task records
        folder_list = TaskRecord.objects.filter(batch=batch, icon="icon-folder").all()
        for folder in folder_list:
            data = os.scandir(folder.full_path)
            bulk_set = []
            for entry in data:
                each = entry.name
                file_type = each.split(".")[-1]
                file_name = ".".join(each.split(".")[:-1])
                if file_type not in ALLOW_TYPE:
                    continue
                full_path = f"{folder.full_path}/{each}"
                
                # Skip if already scraped (any state)
                if skip_scraped:
                    existing = Task.objects.filter(full_path=full_path).exists()
                    if existing:
                        log(f"Skipping (already in history): {each}")
                        skip_count += 1
                        Task.objects.update_or_create(full_path=full_path, defaults={
                            "state": "skipped",
                            "parent_path": folder.full_path,
                            "filename": each,
                            "updated_at": datetime.datetime.now()
                        })
                        skipped_items.append({"name": each, "full_path": full_path})
                        continue
                
                bulk_set.append(TaskRecord(**{
                    "batch": batch,
                    "song_name": file_name,
                    "full_path": full_path,
                    "icon": "icon-music",
                }))
            TaskRecord.objects.bulk_create(bulk_set)

    task_list = TaskRecord.objects.filter(batch=batch).exclude(icon="icon-folder").all()
    total_tasks = len(task_list)
    current_index = 0
    
    # Check for Strict Album Mode
    if select_mode == "strict_album":
        # Group tasks by folder
        tasks_by_folder = defaultdict(list)
        for task in task_list:
            parent_path = os.path.dirname(task.full_path)
            tasks_by_folder[parent_path].append(task)
            
        for folder_path, tasks in tasks_by_folder.items():
            log(f"Processing folder: {folder_path} with {len(tasks)} files")
            
            # Step 1: Voting for Album Name
            album_votes = defaultdict(int)
            artist_votes = defaultdict(int)
            
            for task in tasks:
                try:
                    f = music_tag.load_file(task.full_path)
                    if f['album'].value:
                        album_votes[f['album'].value] += 1
                    if f['artist'].value:
                        artist_votes[f['artist'].value] += 1
                except:
                    pass
            
            # Determine search queries candidates
            queries_to_try = []
            if album_votes:
                # Get the most common album name
                best_album = max(album_votes.items(), key=lambda x: x[1])[0]
                # If usage > 50% or it's the only one
                if album_votes[best_album] > len(tasks) * 0.5:
                    # 1. Try Artist + Album (Highest precision)
                    if artist_votes:
                        best_artist = max(artist_votes.items(), key=lambda x: x[1])[0]
                        queries_to_try.append(f"{best_artist} {best_album}")
                    
                    # 2. Try Album Only (Medium precision)
                    queries_to_try.append(best_album)
            
            # 3. Fallback to folder name (Lowest precision but robust)
            folder_name = os.path.basename(folder_path)
            queries_to_try.append(folder_name)
            
            # Remove duplicates while preserving order
            queries_to_try = list(dict.fromkeys(queries_to_try))

            # Step 2: Search for Album
            remote_album = None
            for search_query in queries_to_try:
                if not search_query: continue
                log(f"Searching Album: {search_query}")
                
                for resource in source_list:
                    if resource == "netease" or True: 
                         remote_album = MusicResource(resource).fetch_album_by_name(search_query)
                         if remote_album:
                             log(f"Found Album: {remote_album['album_name']} by {remote_album['album_artist']}")
                             break
                         else:
                             if resource == "netease":
                                cookie_warning = True
                
                if remote_album:
                    break

            # Step 3: Match and Save
            if remote_album:
                tracks = remote_album['tracks']
                for task in tasks:
                    current_index += 1
                    self.update_state(state='PROGRESS', meta={
                        'current': current_index,
                        'total': total_tasks,
                        'filename': os.path.basename(task.full_path)
                    })
                    matched_song = match_album_song(resource, task.full_path, tracks)
                    
                    if matched_song:
                        # Success
                        task.state = "success"
                        task.song_name = matched_song['name']
                        task.artist_name = matched_song['artist']
                        task.save()
                        
                        log(f"Track Match: {os.path.basename(task.full_path)} -> {matched_song['name']}")
                        success_count += 1
                        success_items.append({
                            "name": os.path.basename(task.full_path),
                            "full_path": task.full_path
                        })

                        # Save ID3 tags (Apply Album Metadata)
                        try:
                            f = music_tag.load_file(task.full_path)
                            # Overlay Album Metadata
                            matched_song['album'] = remote_album['album_name']
                            matched_song['album_img'] = remote_album['album_img']
                            matched_song['year'] = remote_album['year']

                            # Map 'name' to 'title' for save_music
                            matched_song['title'] = matched_song.get('name')

                            # Overwrite Policy Logic
                            if overwrite_policy == 'overwrite_missing':
                                try:
                                    if f['title'].value: matched_song.pop('name', None)
                                    
                                    if f['title'].value: matched_song.pop('title', None)
                                    if f['artist'].value: matched_song.pop('artist', None)
                                    if f['album'].value: matched_song.pop('album', None)
                                    if f['year'].value: matched_song.pop('year', None)
                                    # Album img checking is complex, assume if we have artwork we skip
                                    if f['artwork'].value: matched_song.pop('album_img', None)
                                except Exception as e:
                                    log(f"Overwrite check error: {e}")

                            save_music(f, matched_song, False)
                        except Exception as e:
                            log(f"Save ID3 Error: {e}")

                        parent_path = os.path.dirname(task.full_path)
                        Task.objects.update_or_create(full_path=task.full_path, defaults={
                            "state": task.state,
                            "parent_path": parent_path,
                            "filename": os.path.basename(task.full_path),
                            "song_name": task.song_name,
                            "artist_name": task.artist_name,
                            "error_msg": "",
                            "updated_at": datetime.datetime.now()
                        })
                    else:
                        task.state = "failed"
                        task.save()
                        fail_count += 1
                        log(f"Match Failed: {os.path.basename(task.full_path)}", "error")
                        failed_items.append({
                            "name": os.path.basename(task.full_path),
                            "full_path": task.full_path
                        })
                        
                        # Persist failure to history
                        parent_path = os.path.dirname(task.full_path)
                        Task.objects.update_or_create(full_path=task.full_path, defaults={
                            "state": "failed",
                            "parent_path": parent_path,
                            "filename": os.path.basename(task.full_path),
                            "song_name": task.song_name,
                            "artist_name": task.artist_name,
                            "error_msg": "Match Failed (in Strict Album Mode)",
                            "updated_at": datetime.datetime.now()
                        })
            else:
                log(f"Album not found for {folder_path}, falling back to single song match")
                log(f"Album not found for {folder_path}, falling back to single song match")
                for task in tasks:
                    current_index += 1
                    self.update_state(state='PROGRESS', meta={
                        'current': current_index,
                        'total': total_tasks,
                        'filename': os.path.basename(task.full_path)
                    })
                    s, f, cw = _process_single_task(task, source_list, select_mode, log, overwrite_policy)
                    success_count += s
                    fail_count += f
                    if cw: cookie_warning = True
                    if f > 0:
                        failed_items.append({
                            "name": os.path.basename(task.full_path),
                            "full_path": task.full_path
                        })
                    elif s > 0:
                        success_items.append({
                            "name": os.path.basename(task.full_path),
                            "full_path": task.full_path
                        })

    else:
        # Normal Mode
        for task in task_list:
            current_index += 1
            self.update_state(state='PROGRESS', meta={
                'current': current_index,
                'total': total_tasks,
                'filename': os.path.basename(task.full_path)
            })
            s, f, cw = _process_single_task(task, source_list, select_mode, log, overwrite_policy)
            success_count += s
            fail_count += f
            if cw: cookie_warning = True
            if f > 0:
                failed_items.append({
                    "name": os.path.basename(task.full_path),
                    "full_path": task.full_path
                })
            elif s > 0:
                success_items.append({
                    "name": os.path.basename(task.full_path),
                    "full_path": task.full_path
                })

    return {
        "logs": logs,
        "success_count": success_count,
        "fail_count": fail_count,
        "skip_count": skip_count,
        "cookie_warning": cookie_warning,
        "failed_items": failed_items,
        "success_items": success_items,
        "skipped_items": skipped_items
    }


def _process_single_task(task, source_list, select_mode, log=print, overwrite_policy="overwrite_all"):
    is_match = False
    cw = False
    last_error = ""
    for resource in source_list:
        log(f"Start Matching ({resource}): {os.path.basename(task.full_path)}")
        try:
            is_match = match_song(resource, task.full_path, select_mode, overwrite_policy)
        except Exception as e:
            last_error = str(e)
            log(f"Error: {e}", "error")
            is_match = False
            if "Cookie Invalid" in str(e) and resource == "netease":
                cw = True
            break
        if is_match:
            task.state = "success"
            task.save()
            parent_path = os.path.dirname(task.full_path)
            
            # Manually update updated_at if needed, but auto_now=True handles save()
            # For update_or_create, auto_now=True on model might not trigger if not in defaults?
            # Actually auto_now work on save(), so update_or_create calls save().
            
            Task.objects.update_or_create(full_path=task.full_path, defaults={
                "state": task.state,
                "parent_path": parent_path,
                "filename": os.path.basename(task.full_path),
                "song_name": task.song_name,
                "artist_name": task.artist_name,
                "error_msg": "",  # Clear error on success
                "updated_at": datetime.datetime.now() # Force update timestamp
            })
            log(f"Success: {os.path.basename(task.full_path)}")
            break
        else:
             pass

    if not is_match:
        task.state = "failed"
        task.save()
        log(f"Failed: {os.path.basename(task.full_path)}", "error")
        parent_path = os.path.dirname(task.full_path)
        
        # If no specific exception, default error
        if not last_error:
            last_error = "Match failed (No results found)"
            
        Task.objects.update_or_create(full_path=task.full_path, defaults={
            "state": task.state,
            "parent_path": parent_path,
            "filename": os.path.basename(task.full_path),
            "song_name": task.song_name,
            "artist_name": task.artist_name,
            "error_msg": last_error,
            "updated_at": datetime.datetime.now() # Force update timestamp
        })
        return 0, 1, cw
    return 1, 0, cw


def tidy_folder_task(music_path_list, tidy_config):
    """整理文件夹任务"""
    root_path = tidy_config.get("root_path")
    first_dir = tidy_config.get("first_dir")
    second_dir = tidy_config.get("second_dir")

    if second_dir:
        tidy_map = defaultdict(lambda: defaultdict(list))
        for music_path in music_path_list:
            file = MusicIDS(music_path)
            first_value = getattr(file, first_dir, "未知")
            second_value = getattr(file, second_dir, "未知")
            tidy_map[first_value][second_value].append(music_path)
        for first_value, second_map in tidy_map.items():
            first_path = os.path.join(root_path, first_value)
            if not os.path.exists(first_path):
                os.makedirs(first_path)
            for second_value, music_path_list in second_map.items():
                second_path = os.path.join(first_path, second_value)
                if not os.path.exists(second_path):
                    os.makedirs(second_path)
                for music_path in music_path_list:
                    shutil.move(music_path, second_path)
    else:
        tidy_map = defaultdict(list)
        for music_path in music_path_list:
            file = MusicIDS(music_path)
            first_value = getattr(file, first_dir, "未知")
            tidy_map[first_value].append(music_path)
        for first_value, music_path_list in tidy_map.items():
            first_path = os.path.join(root_path, first_value)
            if not os.path.exists(first_path):
                os.makedirs(first_path)
            for music_path in music_path_list:
                shutil.move(music_path, first_path)
