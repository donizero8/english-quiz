# Repository Guidelines

## Project Structure & Module Organization

This repository is a Docker-first Django listening-quiz application with local Piper TTS.

- `config/`: Django settings, root URLs, and WSGI configuration.
- `quiz/`: domain models, admin configuration, views, routes, TTS integration, migrations, and management commands.
- `templates/quiz/`: public quiz and shared page templates.
- `static/`: frontend CSS and JavaScript.
- `Dockerfile` and `docker-compose.yml`: application runtime, voice-model download, SQLite/audio volumes, and startup commands.
- `app/`: legacy FastAPI prototype; do not extend it unless it is intentionally being removed or migrated.

Place Django tests in `quiz/tests/` or modules named `test_*.py`.

## Build, Test, and Development Commands

Run application commands inside Docker. The Docker executable may require its full Windows path if it is not on `PATH`.

```powershell
docker compose up --build -d
docker compose logs -f tts-app
docker compose exec tts-app python manage.py check
docker compose exec tts-app python manage.py test
docker compose exec tts-app python manage.py makemigrations --check --dry-run
```

The app runs at `http://localhost:8000/`; Django Admin is at `/admin/`. Startup applies migrations and seeds demo data automatically.

## Coding Style & Naming Conventions

Use four-space indentation and PEP 8 conventions for Python. Use `snake_case` for functions and variables, `PascalCase` for Django models/classes, and descriptive migration names such as `0003_add_difficulty.py`. Keep views thin; put speech parsing and synthesis in `quiz/tts.py`. Use Django ORM rather than direct SQLite queries. In scripts and templates, prefer clear IDs/classes and avoid inline JavaScript or CSS.

Conversation scripts use:

```text
Man: Welcome to the library.
Woman: How can I reserve a room?
```

## Testing Guidelines

Use Django’s `TestCase` and test client. Cover model validation, quiz scoring, publishing rules, dialogue parsing, and authenticated CMS actions. Name tests `test_<expected_behavior>`. Avoid regenerating full neural audio in ordinary unit tests; mock synthesis, then reserve a Docker smoke test for Piper integration.

## Commit & Pull Request Guidelines

The repository has no existing commit history, so use concise imperative messages, optionally with Conventional Commit prefixes, for example `feat: add quiz explanations` or `fix: enforce one correct choice`. Pull requests should describe behavior changes, list verification commands, mention migrations or model downloads, and include screenshots for admin or frontend UI changes. Never commit SQLite databases, generated WAV files, credentials, `.venv/`, or Piper model binaries.

## Security & Configuration

Development credentials in `docker-compose.yml` are local-only. Override the admin password and `DJANGO_SECRET_KEY` outside development. Preserve the named Docker volumes when rebuilding so SQLite data and generated audio are not lost.
