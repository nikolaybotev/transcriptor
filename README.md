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
python transcribe.py <audio_file> [model_size] [model_cache_dir]
```

Optional `model_size` values include `tiny.en`, `base.en` (default), and `small.en`. Optional `model_cache_dir` is where Whisper / Hugging Face stores downloaded models; it defaults to the current directory (`.`).
