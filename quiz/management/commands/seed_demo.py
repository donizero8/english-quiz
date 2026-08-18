import os
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from quiz.models import Choice, Conversation, Question
from quiz.tts import create_audio

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not User.objects.filter(username=username).exists():
            if password:
                User.objects.create_superuser(
                    username,
                    os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com"),
                    password,
                )
            else:
                self.stdout.write(self.style.WARNING("Superuser was not created: DJANGO_SUPERUSER_PASSWORD is not set."))
        conversation, created = Conversation.objects.get_or_create(slug="meeting-a-new-friend", defaults={
            "title": "Meeting a New Friend", "description": "Listen to Anna and Ryan meeting for the first time.",
            "script": "Man: Hi, my name is Ryan. What's your name?\nWoman: I'm Anna. Nice to meet you, Ryan.\nMan: Nice to meet you too. Where are you from?\nWoman: I'm from Seattle, but I live in Boston now.",
            "is_published": True,
        })
        if created:
            data = [
                ("What is the woman's name?", ["Anna", "Sarah", "Emily"], 0, "The woman introduces herself as Anna."),
                ("Where does Anna live now?", ["Seattle", "Boston", "Chicago"], 1, "Anna says that she lives in Boston now."),
            ]
            for order, (text, options, correct, explanation) in enumerate(data, 1):
                question = Question.objects.create(conversation=conversation, text=text, explanation=explanation, order=order)
                for index, option in enumerate(options): Choice.objects.create(question=question, text=option, is_correct=index == correct, order=index)
            output = Path("/tmp/demo.wav"); create_audio(conversation.script, output)
            with output.open("rb") as source: conversation.audio.save("conversation-demo.wav", File(source), save=True)
            output.unlink(missing_ok=True)
            self.stdout.write(self.style.SUCCESS("Demo listening quiz created."))
