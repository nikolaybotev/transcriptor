#!/usr/bin/env python3
"""
Transcribe an audio file using faster-whisper.
Usage: python3 transcribe.py <audio_file|-> [model_size] [model_cache_dir]
Use - as audio_file to read raw PCM from stdin: s16le, mono, 16 kHz (e.g. ffmpeg -f s16le …).

Models: tiny.en, base.en, small.en (default: base.en)
model_cache_dir: Hugging Face / whisper model cache (default: ./whisper-models)
"""
import sys
import os

import numpy as np

audio_file = sys.argv[1] if len(sys.argv) > 1 else None
model_size = sys.argv[2] if len(sys.argv) > 2 else 'base.en'
model_cache_dir = sys.argv[3] if len(sys.argv) > 3 else './whisper-models'

if not audio_file:
    print(
        "Usage: transcribe.py <audio_file|-> [model_size] [model_cache_dir]",
        file=sys.stderr,
    )
    sys.exit(1)

if audio_file == "-":
    raw = sys.stdin.buffer.read()
    n = len(raw) - (len(raw) % 2)
    pcm = np.frombuffer(memoryview(raw)[:n], dtype="<i2")
    audio_input = pcm.astype(np.float32) / 32768.0
    print("Loaded raw PCM from stdin", file=sys.stderr)
else:
    audio_input = audio_file

model_cache_dir = os.path.abspath(model_cache_dir)
os.environ['HF_HOME'] = model_cache_dir

from faster_whisper import WhisperModel

cpu_threads = os.cpu_count() or 4
model = WhisperModel(
    model_size,
    device='cpu',
    compute_type='int8',
    download_root=model_cache_dir,
    cpu_threads=cpu_threads,
)

print("Transcribing audio...", file=sys.stderr)

segments, info = model.transcribe(audio_input, beam_size=5)

for segment in segments:
    sys.stdout.write(segment.text)
    sys.stdout.flush()
sys.stdout.write('\n')
