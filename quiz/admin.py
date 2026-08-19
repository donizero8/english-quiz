from pathlib import Path
from django.contrib import admin, messages
from django.core.files import File
from django.utils.html import format_html
from .models import Choice, Conversation, Question
from .tts import create_audio

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "conversation", "order")
    list_filter = ("conversation",)
    inlines = [ChoiceInline]

@admin.action(description="Generate ulang audio untuk conversation terpilih")
def generate_audio(modeladmin, request, queryset):
    for conversation in queryset:
        output = Path("/tmp") / f"conversation-{conversation.pk}.wav"
        try:
            create_audio(
                conversation.script,
                output,
                conversation.voice_speeds,
                conversation.voice_models,
            )
            with output.open("rb") as source:
                conversation.audio.save(f"conversation-{conversation.pk}.wav", File(source), save=True)
            output.unlink(missing_ok=True)
        except Exception as error:
            modeladmin.message_user(request, f"{conversation.title}: {error}", messages.ERROR)
            return
    modeladmin.message_user(request, f"Audio berhasil dibuat untuk {queryset.count()} conversation.")

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "title", "man_voice", "woman_voice", "man_speed", "woman_speed", "is_published",
        "question_count", "has_audio", "updated_at",
    )
    list_filter = ("is_published",)
    search_fields = ("title", "description", "script")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "description", "script")}),
        (
            "Voice Settings",
            {
                "fields": (
                    ("man_voice", "man_speed"),
                    ("woman_voice", "woman_speed"),
                ),
                "description": "Rentang 0.75–1.40. Nilai 1.00 normal; nilai lebih besar lebih cepat.",
            },
        ),
        ("Audio & Publishing", {"fields": ("audio", "audio_preview", "is_published")}),
    )
    readonly_fields = ("audio_preview",)
    actions = [generate_audio]

    @admin.display(description="Dengarkan audio")
    def audio_preview(self, obj):
        if not obj or not obj.audio:
            return "Audio belum tersedia."
        return format_html(
            '<audio controls preload="metadata" '
            'style="display: block; width: clamp(260px, 50vw, 520px); max-width: 70vw;">'
            '<source src="{}" type="audio/wav">'
            "Browser Anda tidak mendukung pemutar audio."
            "</audio>",
            obj.audio.url,
        )

    @admin.display(description="Soal")
    def question_count(self, obj): return obj.questions.count()

    @admin.display(boolean=True, description="Audio")
    def has_audio(self, obj): return bool(obj.audio)

admin.site.site_header = "English Listening Quiz CMS"
admin.site.site_title = "Quiz CMS"
