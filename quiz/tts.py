import re
import subprocess
import tempfile
import wave
from pathlib import Path
from django.conf import settings

VOICE_CONFIG = {
    "MAN": {"model": "en_US-ryan-medium", "length_scale": 1.05},
    "WOMAN": {"model": "en_US-amy-medium", "length_scale": 1.0},
}
LINE_PATTERN = re.compile(r"^(Man|Woman|Voice\s+[AB])\s*:\s*(.+)$", re.IGNORECASE)

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

def synthesize(speaker, sentence, output):
    config = VOICE_CONFIG[speaker]
    model = settings.PIPER_VOICE_DIR / f'{config["model"]}.onnx'
    command = ["python", "-m", "piper", "--model", str(model), "--config", f"{model}.json",
               "--output_file", str(output), "--length-scale", str(config["length_scale"]), "--", sentence]
    proc = subprocess.run(command, capture_output=True, timeout=90)
    if proc.returncode: raise RuntimeError(proc.stderr.decode(errors="replace"))

def combine(parts, output, pause_ms=350):
    with wave.open(str(parts[0]), "rb") as source:
        params = source.getparams(); frames = [source.readframes(source.getnframes())]
    silence = b"\0" * int(params.framerate * pause_ms / 1000) * params.nchannels * params.sampwidth
    for part in parts[1:]:
        with wave.open(str(part), "rb") as source: frames += [silence, source.readframes(source.getnframes())]
    with wave.open(str(output), "wb") as target:
        target.setparams(params); target.writeframes(b"".join(frames))

def create_audio(script, output):
    dialogue = parse_dialogue(script)
    with tempfile.TemporaryDirectory() as folder:
        parts = []
        for index, (speaker, sentence) in enumerate(dialogue):
            part = Path(folder) / f"{index}.wav"; synthesize(speaker, sentence, part); parts.append(part)
        combine(parts, output)
    return len(dialogue)
