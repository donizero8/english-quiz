from __future__ import annotations

import os
import re
import sqlite3
import subprocess
import tempfile
import uuid
import wave
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", BASE_DIR.parent / "data" / "app.db"))
AUDIO_DIR = Path(os.getenv("AUDIO_DIR", BASE_DIR.parent / "generated"))

VOICE_CONFIG = {
    "A": {"name": "Voice A", "model": "en_US-ryan-medium", "length_scale": 1.05},
    "B": {"name": "Voice B", "model": "en_US-amy-medium", "length_scale": 1.0},
}
PIPER_VOICE_DIR = Path(os.getenv("PIPER_VOICE_DIR", BASE_DIR.parent / "voices"))


class GenerateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS generations (
                id TEXT PRIMARY KEY,
                source_text TEXT NOT NULL,
                audio_filename TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )


LINE_PATTERN = re.compile(
    r"^(?:🔊\s*)?(?:\*\*)?Voice\s+([AB])(?:\*\*)?\s*:\s*[\"“”']?(.*?)[\"“”']?\s*$",
    re.IGNORECASE,
)


def parse_dialogue(text: str) -> list[tuple[str, str]]:
    dialogue: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip().replace("**", "")
        if not line:
            continue
        match = LINE_PATTERN.match(line)
        if not match:
            raise ValueError(
                f'Format baris tidak dikenali: "{line}". Gunakan Voice A: teks atau Voice B: teks.'
            )
        speaker, sentence = match.groups()
        sentence = sentence.strip().strip('"“”\'')
        if not sentence:
            raise ValueError(f"Teks untuk Voice {speaker.upper()} tidak boleh kosong.")
        dialogue.append((speaker.upper(), sentence))
    if not dialogue:
        raise ValueError("Dialog tidak boleh kosong.")
    return dialogue


def synthesize_segment(speaker: str, sentence: str, output: Path) -> None:
    config = VOICE_CONFIG[speaker]
    command = [
        "python", "-m", "piper",
        "--model", str(PIPER_VOICE_DIR / f'{config["model"]}.onnx'),
        "--config", str(PIPER_VOICE_DIR / f'{config["model"]}.onnx.json'),
        "--output_file", str(output),
        "--length-scale", str(config["length_scale"]),
        "--", sentence,
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, timeout=60)
    except FileNotFoundError as error:
        raise RuntimeError("Piper tidak tersedia. Jalankan aplikasi melalui Docker.") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode(errors="replace").strip()
        raise RuntimeError(f"Gagal membuat suara: {detail}") from error


def combine_wav(parts: list[Path], output: Path, pause_ms: int = 350) -> None:
    with wave.open(str(parts[0]), "rb") as first:
        params = first.getparams()
        frames = [first.readframes(first.getnframes())]
    silence = b"\x00" * int(params.framerate * pause_ms / 1000) * params.nchannels * params.sampwidth
    for part in parts[1:]:
        with wave.open(str(part), "rb") as source:
            if (source.getnchannels(), source.getsampwidth(), source.getframerate()) != (
                params.nchannels, params.sampwidth, params.framerate
            ):
                raise RuntimeError("Format audio antar suara tidak kompatibel.")
            frames.extend([silence, source.readframes(source.getnframes())])
    with wave.open(str(output), "wb") as target:
        target.setparams(params)
        target.writeframes(b"".join(frames))


def create_audio(dialogue: list[tuple[str, str]], output: Path) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        parts = []
        for index, (speaker, sentence) in enumerate(dialogue):
            part = Path(temp_dir) / f"{index}.wav"
            synthesize_segment(speaker, sentence, part)
            parts.append(part)
        combine_wav(parts, output)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Dialog Voice Generator", lifespan=lifespan)


@app.get("/api/voices")
def voices():
    return [{"id": key, "name": value["name"]} for key, value in VOICE_CONFIG.items()]


@app.post("/api/generations", status_code=201)
def generate(payload: GenerateRequest):
    try:
        dialogue = parse_dialogue(payload.text)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    generation_id = uuid.uuid4().hex
    filename = f"{generation_id}.wav"
    output = AUDIO_DIR / filename
    try:
        create_audio(dialogue, output)
    except RuntimeError as error:
        output.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(error)) from error

    created_at = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute(
            "INSERT INTO generations (id, source_text, audio_filename, created_at) VALUES (?, ?, ?, ?)",
            (generation_id, payload.text, filename, created_at),
        )
    return {
        "id": generation_id,
        "audio_url": f"/api/audio/{generation_id}",
        "created_at": created_at,
        "lines": len(dialogue),
    }


@app.get("/api/audio/{generation_id}")
def audio(generation_id: str):
    with connect() as db:
        item = db.execute(
            "SELECT audio_filename FROM generations WHERE id = ?", (generation_id,)
        ).fetchone()
    if not item:
        raise HTTPException(status_code=404, detail="Audio tidak ditemukan.")
    path = AUDIO_DIR / item["audio_filename"]
    if not path.is_file():
        raise HTTPException(status_code=404, detail="File audio tidak ditemukan.")
    return FileResponse(path, media_type="audio/wav", filename="conversation.wav")


@app.get("/api/generations")
def history():
    with connect() as db:
        items = db.execute(
            "SELECT id, source_text, created_at FROM generations ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    return [
        {**dict(item), "audio_url": f'/api/audio/{item["id"]}'} for item in items
    ]


app.mount("/", StaticFiles(directory=BASE_DIR / "static", html=True), name="static")
