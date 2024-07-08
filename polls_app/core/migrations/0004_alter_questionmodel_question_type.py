# Generated by Django 5.0.5 on 2024-05-24 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_choicemodel_created_on_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionmodel',
            name='question_type',
            field=models.CharField(choices=[('Single choice', 'Single choice'), ('Multiple choices', 'Multiple choices'), ('Open answer', 'Open answer')], max_length=16),
        ),
    ]