#!/usr/bin/env python3
"""
Pre-download faster-whisper English models into a Hugging Face-style cache directory.

These correspond to repos on Hugging Face (e.g. Systran/faster-whisper-base.en).
Default cache directory is ./whisper-models next to this script.

Usage:
  python3 download_models.py [cache_dir]
  python3 download_models.py --help
"""
import argparse
import os
import sys

# Models present in a typical dev setup (matches transcribe.py examples).
DEFAULT_MODELS = ("tiny.en", "base.en", "small.en")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download faster-whisper models into a local cache directory.",
    )
    parser.add_argument(
        "cache_dir",
        nargs="?",
        default=None,
        help="Directory for HF_HOME / Whisper downloads (default: <repo>/whisper-models)",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if args.cache_dir is None:
        cache_dir = os.path.join(script_dir, "whisper-models")
    else:
        cache_dir = args.cache_dir

    cache_dir = os.path.abspath(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    os.environ["HF_HOME"] = cache_dir

    from faster_whisper import WhisperModel

    for name in DEFAULT_MODELS:
        print(f"Downloading {name} into {cache_dir} …", file=sys.stderr)
        WhisperModel(
            name,
            device="cpu",
            compute_type="int8",
            download_root=cache_dir,
        )
        print(f"  OK: {name}", file=sys.stderr)

    print(cache_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
