# Generated by Django 5.1.2 on 2024-11-15 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppCodingNexus', '0009_userprofile_deletion_requested_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Courses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_name', models.CharField(max_length=100)),
                ('course_description', models.TextField(blank=True, null=True)),
                ('course_image', models.ImageField(default='default.jpg', upload_to='course_images/')),
            ],
        ),
    ]
