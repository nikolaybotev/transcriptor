#!/usr/bin/env python3
"""
Transcribe an audio file using faster-whisper.
Usage: python3 transcribe.py <audio_file> [model_size] [model_cache_dir]
Models: tiny.en, base.en, small.en (default: base.en)
model_cache_dir: Hugging Face / whisper model cache (default: current directory)
"""
import sys
import os

audio_file = sys.argv[1] if len(sys.argv) > 1 else None
model_size = sys.argv[2] if len(sys.argv) > 2 else 'base.en'
model_cache_dir = sys.argv[3] if len(sys.argv) > 3 else './whisper-models'

if not audio_file:
    print(
        "Usage: transcribe.py <audio_file> [model_size] [model_cache_dir]"
    )
    sys.exit(1)

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

segments, info = model.transcribe(audio_file, beam_size=5)

text = ' '.join(segment.text.strip() for segment in segments)
print(text)
