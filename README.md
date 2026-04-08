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

### Memory

How RAM behaves depends on **how you feed audio** (file path vs raw stdin) and **how long** the source is. Figures below are from one machine; model variant, threads, and OS will move them.

**Summary**

- Startup memory spike scales **linearly** with audio duration—about **4.5 GB per hour** (see table).
- Preloading raw audio samples for Whisper (stdin path) is **less memory-efficient**; it **roughly doubles** steady-state memory use during transcription compared to passing a media file path.

#### Peak RSS vs duration

Peak usage hits when the **feature pipeline** runs (building mel / STFT for the encoder). It scales **roughly linearly** with source length and is **similar whether the input is an MP3 path or pre-decoded stdin**—container format is not the main driver.

Assume **~300 MB** (~0.3 GB) for the **int8 model** in RAM; the table subtracts that so the rest is mostly spectrogram-related buffers.

| Duration | Peak RSS (approx.) | Rel. duration (× 30 min) | Peak minus ~300 MB model (GB) | Rel. Δ peak (× 30 min Δ) |
|----------|-------------------:|-------------------------:|---------------------------------:|-------------------------:|
| 30 min   | 2.5 GB | 1× | 2.2 | 1× |
| 1 hour   | 4.7 GB | 2× | 4.4 | 2× |
| 2 h 18 min (full video) | 10.2 GB | 4.6× | 9.9 | 4.5× |

The “minus ~300 MB” column treats **0.3 GB** as the int8 model only; any other tiny fixed overhead is rolled into that variable bucket.

**Linearity:** From **30 min → 1 h**, duration and variable peak **both double** (1×→2× and 2.2 GB→4.4 GB)—exactly linear after removing the model floor. The **full video** (4.6× the 30-minute row) would predict **4.6 × 2.2 ≈ 10.1 GB** variable; **9.9 GB** measured is within **~2%**—still linear for practical estimates.

#### Why peak grows with length

Whisper does not eat raw samples directly. Audio becomes a **log-mel spectrogram**: an **STFT** over overlapping windows, then **mel** filters to a 2D “image” over time. Long files mean large feature tensors (and STFT intermediates) in memory, so peak RSS tracks duration whether audio came from PyAV (MP3 path) or a numpy buffer (stdin).

#### Raw stdin vs MP3 path

Pre-decoding to `.raw` or piping **s16le** avoids **a few seconds** of in-process decode/transcode (PyAV). It does **not** remove the big mel/STFT peak above.

After the spike, **steady-state RSS** was about **~1.4 GB** with stdin and **~700 MB** with an **MP3 path**—stdin keeps a full **float32** waveform in Python on top of the model. For long jobs, prefer passing the **media file path** if you want lower steady-state memory; raw stdin is mainly a **latency / CPU** win on decode, not a RAM win.
