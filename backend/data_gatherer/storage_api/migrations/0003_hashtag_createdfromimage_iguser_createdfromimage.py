# Generated by Django 4.2.14 on 2024-08-02 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storage_api', '0002_alter_iguser_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='hashtag',
            name='createdFromImage',
            field=models.ForeignKey(default=15, on_delete=django.db.models.deletion.CASCADE, to='storage_api.image'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iguser',
            name='createdFromImage',
            field=models.ForeignKey(default=15, on_delete=django.db.models.deletion.CASCADE, to='storage_api.image'),
            preserve_default=False,
        ),
    ]
