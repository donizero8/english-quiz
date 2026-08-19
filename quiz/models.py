from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .voices import DEFAULT_VOICE_MODELS, voice_choices

class Conversation(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    script = models.TextField(help_text="Gunakan format Man: ... dan Woman: ...")
    man_voice = models.CharField(
        max_length=64,
        choices=voice_choices("MAN"),
        default=DEFAULT_VOICE_MODELS["MAN"],
    )
    woman_voice = models.CharField(
        max_length=64,
        choices=voice_choices("WOMAN"),
        default=DEFAULT_VOICE_MODELS["WOMAN"],
    )
    man_speed = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0.75")), MaxValueValidator(Decimal("1.40"))],
        help_text="1.00 = normal; nilai lebih besar membuat suara lebih cepat.",
    )
    woman_speed = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("1.10"),
        validators=[MinValueValidator(Decimal("0.75")), MaxValueValidator(Decimal("1.40"))],
        help_text="1.00 = normal; nilai lebih besar membuat suara lebih cepat.",
    )
    audio = models.FileField(upload_to="conversations/", blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self): return self.title

    @property
    def voice_speeds(self):
        return {"MAN": self.man_speed, "WOMAN": self.woman_speed}

    @property
    def voice_models(self):
        return {"MAN": self.man_voice, "WOMAN": self.woman_voice}

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
