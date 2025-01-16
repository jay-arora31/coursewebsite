# Generated by Django 5.1.4 on 2025-01-14 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_remove_submodule_order_remove_video_order_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='submodule',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='submodule',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='video',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]