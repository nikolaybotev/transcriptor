#!/usr/bin/env python3
"""
Transcribe an audio file using faster-whisper.
Usage: python3 transcribe.py <audio_file> [model_size]
Models: tiny.en, base.en, small.en (default: base.en)
"""
import sys
import os

# Use models from SSD
os.environ['HF_HOME'] = '/mnt/claw/whisper-models'

from faster_whisper import WhisperModel

audio_file = sys.argv[1] if len(sys.argv) > 1 else None
model_size = sys.argv[2] if len(sys.argv) > 2 else 'base.en'

if not audio_file:
    print("Usage: transcribe.py <audio_file> [model_size]")
    sys.exit(1)

model = WhisperModel(model_size, device='cpu', compute_type='int8',
                     download_root='/mnt/claw/whisper-models')

segments, info = model.transcribe(audio_file, beam_size=5)

text = ' '.join(segment.text.strip() for segment in segments)
print(text)
