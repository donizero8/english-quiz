# Repository Guidelines

## Project Structure & Module Organization

This is a Docker-first Django listening-quiz application with local Piper TTS.

- `config/`: Django settings, root URLs, and WSGI configuration.
- `quiz/`: models, Admin, views, routes, Piper integration, migrations, seed command, and tests.
- `templates/quiz/`: Academy-style catalog and quiz templates.
- `static/`: public frontend CSS and JavaScript.
- `Dockerfile` and `docker-compose.yml`: runtime, Piper model download, persistent SQLite/audio volumes, and startup.

Keep the allowed voice registry in `quiz/voices.py`. Keep speech parsing, punctuation rules, per-actor voice/speed selection, synthesis, and WAV assembly in `quiz/tts.py`. Conversation speed values are intuitive multipliers; convert them to Piper with `length_scale = 1 / speed`.

## Build, Test, and Development Commands

Run application commands inside Docker:

```powershell
docker compose up --build -d
docker compose logs -f tts-app
docker compose exec tts-app python manage.py check
docker compose exec tts-app python manage.py test
docker compose exec tts-app python manage.py test quiz.tests
docker compose exec tts-app python manage.py makemigrations --check --dry-run
```

The frontend runs at `http://localhost:8000/`; Django Admin is at `/admin/`. Startup applies migrations and seeds demo data idempotently.

## Coding Style & Naming Conventions

Use four-space indentation and PEP 8 for Python. Use `snake_case` for functions and variables, `PascalCase` for classes/models, and descriptive migration names. Keep views thin and use the Django ORM instead of direct SQLite queries. Prefer clear template classes/IDs and avoid inline CSS or JavaScript unless Django Admin rendering requires a small self-contained style.

Conversation scripts use one actor per line:

```text
Man: Welcome to the library.
Woman: How can I reserve a room?
```

## Testing Guidelines

Use Django `TestCase` or `SimpleTestCase`; name tests `test_<expected_behavior>`. Cover model validation, scoring, publishing, dialogue parsing, punctuation splitting, voice-speed conversion, and authenticated Admin/API behavior. Mock synthesis in unit tests. Use a Docker smoke test for real Piper/WAV integration because model inference is slower. TTS and model tests live in `quiz/tests/`.

## Commit & Pull Request Guidelines

Follow the existing Conventional Commit style, for example `feat: add audio preview` or `fix: preserve punctuation prosody`. Pull requests should describe behavior, list verification commands, identify migrations or model changes, and include screenshots for UI/Admin changes. Never commit SQLite databases, generated WAV files, credentials, `.env`, `.venv/`, or Piper models.

## Security & Configuration

Copy `.env.example` to the ignored `.env` file and replace all example values. Do not place credentials directly in `docker-compose.yml`. Preserve named Docker volumes during rebuilds so CMS data and audio are not lost.
