# English Listening Quiz

A Docker-first Django application for authoring and delivering English listening quizzes. Editors manage conversations, questions, choices, publishing, and audio in Django Admin. Speech is generated locally with Piper and stored with SQLite-backed quiz data in persistent Docker volumes.

## Current Features

- Django CMS with `Conversation`, `Question`, and `Choice` models
- Single-answer quiz scoring with answer explanations
- Academy-style responsive frontend
- American English neural TTS:
  - `Man` → `en_US-ryan-medium`
  - `Woman` → `en_US-amy-medium`
- WAV generation from Django Admin and an inline Admin audio player
- Punctuation-aware pauses for commas, periods, ellipses, questions, exclamations, hyphens, colons, and semicolons
- Published quiz catalog with persistent SQLite and generated-audio volumes

## Run with Docker

```powershell
Copy-Item .env.example .env
# Replace the example secrets in .env
docker compose up --build -d
```

Open:

- Frontend: http://localhost:8000/
- Django Admin: http://localhost:8000/admin/

On startup, Docker applies migrations, creates the configured superuser when needed, seeds a demo quiz, and starts Django on port 8000. The first image build downloads both Piper models.

## Authoring a Quiz

Use one actor per line:

```text
Man: Hello, John. Are you using this room?
Woman: Not yet... but I reserved it for three o'clock.
```

Create questions and choices under the conversation, mark exactly one choice correct, then enable **Is published**. To create or refresh the WAV, select conversations in the Admin list and run **Generate ulang audio untuk conversation terpilih**. The edit page includes a player under **Dengarkan audio**.

Supported pause timings are approximately: comma 180 ms, period 380 ms, ellipsis 700 ms, question 420 ms, exclamation 320 ms, hyphen 280–320 ms, colon 300 ms, semicolon 320 ms, and actor changes at least 500 ms. Existing WAV files must be regenerated after script or TTS-rule changes. Very short isolated utterances may sound abrupt because Piper loses surrounding prosody when punctuation is synthesized as separate chunks.

## Endpoints

- `GET /` — published quiz catalog
- `GET /quiz/<slug>/` — listening quiz
- `POST /quiz/<slug>/submit/` — score submitted choices
- `POST /api/conversations/<id>/generate-audio/` — staff-only Django audio generation
- `/admin/` — Django CMS

## Development Commands

```powershell
docker compose logs -f tts-app
docker compose exec tts-app python manage.py check
docker compose exec tts-app python manage.py test
docker compose exec tts-app python manage.py test quiz.tests
docker compose exec tts-app python manage.py makemigrations --check --dry-run
```

Do not commit `.env`, SQLite databases, generated WAV files, `.venv/`, or Piper model binaries.
