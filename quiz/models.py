from django.core.exceptions import ValidationError
from django.db import models

class Conversation(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    script = models.TextField(help_text="Gunakan format Man: ... dan Woman: ...")
    audio = models.FileField(upload_to="conversations/", blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title

class Question(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self): return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def clean(self):
        if self.is_correct and self.question_id:
            if Choice.objects.filter(question_id=self.question_id, is_correct=True).exclude(pk=self.pk).exists():
                raise ValidationError("Setiap soal hanya boleh memiliki satu jawaban benar.")

    def __str__(self): return self.text
