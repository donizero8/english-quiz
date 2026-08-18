from pathlib import Path
from django.contrib import admin, messages
from django.core.files import File
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
            create_audio(conversation.script, output)
            with output.open("rb") as source:
                conversation.audio.save(f"conversation-{conversation.pk}.wav", File(source), save=True)
            output.unlink(missing_ok=True)
        except Exception as error:
            modeladmin.message_user(request, f"{conversation.title}: {error}", messages.ERROR)
            return
    modeladmin.message_user(request, f"Audio berhasil dibuat untuk {queryset.count()} conversation.")

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "question_count", "has_audio", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "description", "script")
    prepopulated_fields = {"slug": ("title",)}
    actions = [generate_audio]

    @admin.display(description="Soal")
    def question_count(self, obj): return obj.questions.count()

    @admin.display(boolean=True, description="Audio")
    def has_audio(self, obj): return bool(obj.audio)

admin.site.site_header = "English Listening Quiz CMS"
admin.site.site_title = "Quiz CMS"
