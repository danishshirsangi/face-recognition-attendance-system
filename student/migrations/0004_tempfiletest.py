# Generated by Django 4.1.3 on 2023-02-01 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_alter_student_img1_alter_student_img2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TempFileTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(upload_to='mediaimage/')),
            ],
        ),
    ]