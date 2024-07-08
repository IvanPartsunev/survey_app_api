# Generated by Django 5.0.5 on 2024-05-23 19:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_productmodel_owner_alter_questionmodel_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='choicemodel',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='choicemodel',
            name='edited_on',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='commentmodel',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='commentmodel',
            name='edited_on',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='productmodel',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='productmodel',
            name='edited_on',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='created_on',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='edited_on',
            field=models.DateField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='questionmodel',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='core.productmodel'),
        ),
    ]