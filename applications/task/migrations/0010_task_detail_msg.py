# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0009_taskrecord_error_msg'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='detail_msg',
            field=models.TextField(default=''),
        ),
    ]
