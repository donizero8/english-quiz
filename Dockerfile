FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /app/voices \
    && python -m piper.download_voices --data-dir /app/voices \
        en_US-ryan-medium en_US-amy-medium
RUN python -m piper.download_voices --data-dir /app/voices \
        en_US-hfc_male-medium en_US-hfc_female-medium
COPY manage.py .
COPY config ./config
COPY quiz ./quiz
COPY templates ./templates
COPY static ./static

RUN mkdir -p /app/data /app/generated
ENV DATABASE_PATH=/app/data/app.db \
    AUDIO_DIR=/app/generated \
    PIPER_VOICE_DIR=/app/voices
EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_demo && python manage.py runserver 0.0.0.0:8000 --noreload"]
