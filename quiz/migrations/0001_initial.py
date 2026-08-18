from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Conversation", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=200)), ("slug", models.SlugField(unique=True)),
            ("description", models.TextField(blank=True)),
            ("script", models.TextField(help_text="Gunakan format Voice A: ... dan Voice B: ...")),
            ("audio", models.FileField(blank=True, upload_to="conversations/")),
            ("is_published", models.BooleanField(default=False)),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
        ], options={"ordering": ["-created_at"]}),
        migrations.CreateModel(name="Question", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("text", models.CharField(max_length=500)), ("explanation", models.TextField(blank=True)),
            ("order", models.PositiveIntegerField(default=0)),
            ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="quiz.conversation")),
        ], options={"ordering": ["order", "id"]}),
        migrations.CreateModel(name="Choice", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("text", models.CharField(max_length=300)), ("is_correct", models.BooleanField(default=False)),
            ("order", models.PositiveIntegerField(default=0)),
            ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="choices", to="quiz.question")),
        ], options={"ordering": ["order", "id"]}),
    ]
