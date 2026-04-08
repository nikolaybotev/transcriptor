# Transcriptor

Transcribe audio files locally with [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

## Prerequisites

- Python 3.9 or newer (3.10+ recommended)

## Setup

### 1. Create a virtual environment

From the project directory:

```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment

**macOS / Linux:**

```bash
source .venv/bin/activate
```

**Windows (Command Prompt):**

```cmd
.venv\Scripts\activate.bat
```

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

Your shell prompt should show `(.venv)` when the environment is active.

### 3. Install dependencies

With the venv activated:

```bash
pip install -r requirements.txt
```

To leave the virtual environment later, run `deactivate`.

## Usage

```bash
python transcribe.py <audio_file|-> [model_size] [model_cache_dir]
```

Use `-` as `audio_file` to read **raw PCM** from stdin: **s16le, mono, 16 kHz** (same as `ffmpeg -f s16le -ac 1 -ar 16000`). Example: `cat audio.s16le | python transcribe.py -` or `ffmpeg -i track.mp3 -f s16le -ac 1 -ar 16000 pipe:1 | python transcribe.py -`.

Optional `model_size` values include `tiny.en`, `base.en` (default), and `small.en`. Optional `model_cache_dir` is where Whisper / Hugging Face stores downloaded models; it defaults to `./whisper-models`.

### Memory: raw stdin vs passing an MP3 path

Pre-decoding to a `.raw` file (or piping s16le from ffmpeg) **skips the few seconds** faster-whisper would otherwise spend decoding and transcoding the MP3 inside PyAV. In practice, though:

- **Peak memory** during the run can **still reach on the order of ~9 GB** (same ballpark as with an MP3 path)—the heavy mel/STFT path is unchanged.
- **Steady-state RSS after that spike** was roughly **~1.4 GB** when feeding pre-decoded raw via stdin, versus **~700 MB** when passing the **MP3 file path** and letting the library decode it. The stdin path builds a full **float32 waveform** in Python (`numpy`) in addition to the model’s own buffers, which roughly doubles retained audio-related memory versus streaming decode from a file.

So raw input is mainly a **latency / CPU** win for the decode step, not a way to cut peak RAM; for lower steady-state memory on long files, prefer passing the **media file path** when possible.
