import re
import subprocess
import tempfile
import wave
from pathlib import Path
from django.conf import settings

from .voices import DEFAULT_VOICE_MODELS, VOICE_MODELS

DEFAULT_VOICE_SPEEDS = {"MAN": 1.0, "WOMAN": 1.10}
LINE_PATTERN = re.compile(r"^(Man|Woman|Voice\s+[AB])\s*:\s*(.+)$", re.IGNORECASE)
PUNCTUATION_PATTERN = re.compile(
    r"\.{3}|[.!?;:,]|(?<=[A-Za-z])[-–—](?=[A-Za-z])"
)
PUNCTUATION_PAUSES = {
    ",": 180,
    ".": 380,
    "...": 700,
    "?": 420,
    "!": 320,
    "-": 280,
    "–": 280,
    "—": 320,
    ":": 300,
    ";": 320,
}
SPEAKER_PAUSE_MS = 500

def parse_dialogue(text):
    result = []
    for raw in text.splitlines():
        if not raw.strip(): continue
        match = LINE_PATTERN.match(raw.strip())
        if not match: raise ValueError(f'Format baris tidak dikenali: "{raw.strip()}"')
        actor = match.group(1).upper()
        actor = {"VOICE A": "MAN", "VOICE B": "WOMAN"}.get(actor, actor)
        result.append((actor, match.group(2).strip()))
    if not result: raise ValueError("Dialog tidak boleh kosong.")
    return result


def split_by_punctuation(sentence):
    """Return speech chunks and the pause that follows each chunk."""
    chunks = []
    start = 0
    for match in PUNCTUATION_PATTERN.finditer(sentence):
        punctuation = match.group()
        spoken_punctuation = "" if punctuation in {"-", "–", "—"} else punctuation
        chunk = f"{sentence[start:match.start()]}{spoken_punctuation}".strip()
        if chunk:
            chunks.append((chunk, PUNCTUATION_PAUSES[punctuation]))
        start = match.end()

    remainder = sentence[start:].strip()
    if remainder:
        chunks.append((remainder, 0))
    return chunks or [(sentence.strip(), 0)]

def speed_to_length_scale(speed):
    speed = float(speed)
    if speed <= 0:
        raise ValueError("Voice speed harus lebih besar dari 0.")
    return round(1 / speed, 4)


def synthesize(speaker, sentence, output, speed=1.0, voice_model=None):
    voice_model = voice_model or DEFAULT_VOICE_MODELS[speaker]
    if voice_model not in VOICE_MODELS[speaker]:
        raise ValueError(f'Voice "{voice_model}" tidak valid untuk {speaker.title()}.')
    model = settings.PIPER_VOICE_DIR / f"{voice_model}.onnx"
    command = ["python", "-m", "piper", "--model", str(model), "--config", f"{model}.json",
               "--output_file", str(output), "--length-scale", str(speed_to_length_scale(speed)), "--", sentence]
    proc = subprocess.run(command, capture_output=True, timeout=90)
    if proc.returncode: raise RuntimeError(proc.stderr.decode(errors="replace"))

def combine(parts, pauses, output):
    with wave.open(str(parts[0]), "rb") as source:
        params = source.getparams(); frames = [source.readframes(source.getnframes())]
    for index, part in enumerate(parts[1:]):
        pause_ms = pauses[index]
        silence = (
            b"\0"
            * int(params.framerate * pause_ms / 1000)
            * params.nchannels
            * params.sampwidth
        )
        with wave.open(str(part), "rb") as source:
            frames += [silence, source.readframes(source.getnframes())]
    with wave.open(str(output), "wb") as target:
        target.setparams(params); target.writeframes(b"".join(frames))

def create_audio(script, output, voice_speeds=None, voice_models=None):
    dialogue = parse_dialogue(script)
    voice_speeds = {**DEFAULT_VOICE_SPEEDS, **(voice_speeds or {})}
    voice_models = {**DEFAULT_VOICE_MODELS, **(voice_models or {})}
    with tempfile.TemporaryDirectory() as folder:
        parts = []
        pauses = []
        for dialogue_index, (speaker, sentence) in enumerate(dialogue):
            chunks = split_by_punctuation(sentence)
            for chunk, pause_ms in chunks:
                part = Path(folder) / f"{len(parts)}.wav"
                synthesize(
                    speaker,
                    chunk,
                    part,
                    voice_speeds[speaker],
                    voice_models[speaker],
                )
                parts.append(part)
                pauses.append(pause_ms)
            if dialogue_index < len(dialogue) - 1:
                pauses[-1] = max(pauses[-1], SPEAKER_PAUSE_MS)
        combine(parts, pauses, output)
    return len(dialogue)
