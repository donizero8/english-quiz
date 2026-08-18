# English Listening Quiz

A Docker-first Django application for creating English listening quizzes. Editors manage conversations, single-answer questions, and choices in Django Admin. Audio is generated locally with Piper using separate American English male and female voices.

## Features

- Django CMS backed by SQLite
- Conversation scripts using `Man:` and `Woman:` actors
- Local neural TTS with `en_US-ryan-medium` and `en_US-amy-medium`
- Published quiz catalog, audio player, scoring, and answer explanations
- Persistent Docker volumes for SQLite data and generated WAV files

## Run with Docker

Create the local environment file and replace the example secrets:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

Open:

- Quiz frontend: http://localhost:8000/
- Django Admin: http://localhost:8000/admin/

The container downloads the Piper models during the first build, applies migrations, seeds a demo quiz, and starts Django on port 8000.

## Conversation Format

```text
Man: Hi, is this study room available?
Woman: Yes, but you need to reserve it online.
```

In Django Admin, select one or more conversations and run **Generate ulang audio untuk conversation terpilih** from the Actions menu.

## Useful Commands

```powershell
docker compose logs -f tts-app
docker compose exec tts-app python manage.py check
docker compose exec tts-app python manage.py test
docker compose exec tts-app python manage.py makemigrations --check --dry-run
```

SQLite databases, generated audio, local environment files, virtual environments, and Piper model binaries must not be committed.
