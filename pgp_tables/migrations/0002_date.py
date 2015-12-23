from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gpg', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='keysigningparty',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='keysigningparty',
            name='date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
