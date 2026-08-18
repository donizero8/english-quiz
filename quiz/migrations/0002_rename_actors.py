from django.db import migrations, models


def rename_actors(apps, schema_editor):
    Conversation = apps.get_model("quiz", "Conversation")
    for conversation in Conversation.objects.all():
        script = conversation.script.replace("Voice A:", "Man:").replace("Voice B:", "Woman:")
        script = script.replace("voice a:", "Man:").replace("voice b:", "Woman:")
        if script != conversation.script:
            conversation.script = script
            conversation.save(update_fields=["script"])


class Migration(migrations.Migration):
    dependencies = [("quiz", "0001_initial")]
    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="script",
            field=models.TextField(help_text="Gunakan format Man: ... dan Woman: ..."),
        ),
        migrations.RunPython(rename_actors, migrations.RunPython.noop),
    ]
