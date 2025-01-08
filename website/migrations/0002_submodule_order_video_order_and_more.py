# Generated by Django 5.1.4 on 2024-12-28 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submodule',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='video',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='submodule',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='submodule',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='video',
            name='duration',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='video',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
