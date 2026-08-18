import json
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import Choice, Conversation
from .tts import create_audio

def home(request):
    conversations = Conversation.objects.filter(is_published=True).prefetch_related("questions__choices")
    return render(request, "quiz/home.html", {"conversations": conversations})

def quiz_detail(request, slug):
    conversation = get_object_or_404(
        Conversation.objects.prefetch_related("questions__choices"), slug=slug, is_published=True
    )
    return render(request, "quiz/detail.html", {"conversation": conversation})

@require_POST
def submit_quiz(request, slug):
    conversation = get_object_or_404(Conversation, slug=slug, is_published=True)
    answers = json.loads(request.body or "{}").get("answers", {})
    questions = conversation.questions.prefetch_related("choices")
    results, score = [], 0
    for question in questions:
        selected_id = str(answers.get(str(question.id), ""))
        correct = next((choice for choice in question.choices.all() if choice.is_correct), None)
        is_correct = correct is not None and selected_id == str(correct.id)
        score += int(is_correct)
        results.append({"question_id": question.id, "correct": is_correct,
                        "correct_choice_id": correct.id if correct else None,
                        "explanation": question.explanation})
    return JsonResponse({"score": score, "total": len(results), "results": results})

@require_POST
def generate_conversation_audio(request, pk):
    if not request.user.is_staff: return JsonResponse({"detail": "Unauthorized"}, status=403)
    conversation = get_object_or_404(Conversation, pk=pk)
    output = settings.MEDIA_ROOT / "conversations" / f"conversation-{pk}.wav"
    output.parent.mkdir(parents=True, exist_ok=True)
    try: lines = create_audio(conversation.script, output)
    except (ValueError, RuntimeError) as error: return JsonResponse({"detail": str(error)}, status=422)
    conversation.audio.name = f"conversations/conversation-{pk}.wav"; conversation.save(update_fields=["audio"])
    return JsonResponse({"audio_url": conversation.audio.url, "lines": lines})
