from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0007_auto_20260111_2347'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='error_msg',
            field=models.TextField(blank=True, default='', verbose_name='Error Message'),
        ),
        migrations.AddField(
            model_name='taskrecord',
            name='error_msg',
            field=models.TextField(blank=True, default='', verbose_name='Error Message'),
        ),
    ]
