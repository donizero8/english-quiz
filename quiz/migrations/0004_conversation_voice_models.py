from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("quiz", "0003_conversation_voice_speeds")]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="man_voice",
            field=models.CharField(
                choices=[
                    ("en_US-ryan-medium", "Ryan — American Male"),
                    ("en_US-hfc_male-medium", "HFC Male — American Male"),
                ],
                default="en_US-ryan-medium",
                max_length=64,
            ),
        ),
        migrations.AddField(
            model_name="conversation",
            name="woman_voice",
            field=models.CharField(
                choices=[
                    ("en_US-amy-medium", "Amy — American Female"),
                    ("en_US-hfc_female-medium", "HFC Female — American Female"),
                ],
                default="en_US-amy-medium",
                max_length=64,
            ),
        ),
    ]
