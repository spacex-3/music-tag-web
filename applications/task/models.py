from django.db import models


class Task(models.Model):
    song_name = models.CharField(max_length=255, default="")
    artist_name = models.CharField(max_length=255, default="")

    full_path = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=255, default="wait")
    parent_path = models.CharField(max_length=255, default="")
    filename = models.CharField(max_length=255, default="")
    error_msg = models.TextField(default="")
    detail_msg = models.TextField(default="")  # What was written on success (e.g., "写入: 专辑, 艺术家, 歌词")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class TaskRecord(models.Model):
    song_name = models.CharField(max_length=255, default="")
    artist_name = models.CharField(max_length=255, default="")
    full_path = models.CharField(max_length=255, default="")
    tag_source = models.CharField(max_length=255, default="")
    icon = models.CharField(max_length=255, default="icon-folder")
    state = models.CharField(max_length=255, default="wait")
    extra = models.TextField(default="")
    error_msg = models.TextField(default="")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    batch = models.CharField(max_length=255, default="")
