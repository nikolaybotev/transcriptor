#!/usr/bin/env bash
# Transcribe audio with automatic chunking (30-minute chunks, no overlap).
# Sequential chunking and concatenation with spaces between chunk transcripts.
#
# Usage: transcribe-with-chunking.sh <audio_file> <output_txt> [model_size] [model_cache_dir]
#
# Example:
#   ./transcribe-with-chunking.sh /tmp/video.mp3 /tmp/video.txt tiny.en ./whisper-models

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRANSCRIBE_PY="${SCRIPT_DIR}/transcribe.py"

usage() {
  echo "Usage: $0 <audio_file> <output_txt> [model_size] [model_cache_dir]" >&2
  exit 1
}

[[ $# -lt 2 ]] && usage

audio_file="$1"
output_txt="$2"
model_size="${3:-tiny.en}"
model_cache_dir="${4:-${SCRIPT_DIR}/whisper-models}"

if [[ ! -f "$audio_file" ]]; then
  echo "Error: audio file not found: $audio_file" >&2
  exit 1
fi

if [[ ! -f "$TRANSCRIBE_PY" ]]; then
  echo "Error: transcriptor script not found: $TRANSCRIBE_PY" >&2
  exit 1
fi

chunks_dir="$(mktemp -d "${TMPDIR:-/tmp}/transcribe-chunks-XXXXXX")"
cleanup() { rm -rf "$chunks_dir"; }
trap cleanup EXIT

duration_sec="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$audio_file" | tr -d '\r')"
if [[ -z "$duration_sec" ]] || ! awk "BEGIN { exit !($duration_sec > 0) }" 2>/dev/null; then
  echo "Error: could not read duration from: $audio_file" >&2
  exit 1
fi

mins="$(printf '%.0f' "$(awk "BEGIN { print int($duration_sec / 60) }")")"
secs="$(printf '%.0f' "$(awk "BEGIN { print int($duration_sec % 60) }")")"
echo "Audio duration: ${duration_sec}s (${mins}m ${secs}s)" >&2

echo "Chunking audio into $chunks_dir..." >&2
if ! ffmpeg -y -i "$audio_file" -f segment -segment_time 1800 -c copy \
  "${chunks_dir}/chunk-%03d.mp3" >/dev/null 2>&1; then
  echo "Error: ffmpeg segment failed" >&2
  exit 1
fi
echo "Chunking complete." >&2

shopt -s nullglob
chunks=( "${chunks_dir}"/chunk-*.mp3 )
shopt -u nullglob

if [[ ${#chunks[@]} -eq 0 ]]; then
  echo "Error: no chunks created" >&2
  exit 1
fi

IFS=$'\n' sorted_chunks=( $(printf '%s\n' "${chunks[@]}" | sort) )
unset IFS

echo "Created ${#sorted_chunks[@]} chunks." >&2

run_transcribe() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 3600 python3 "$TRANSCRIBE_PY" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout 3600 python3 "$TRANSCRIBE_PY" "$@"
  else
    python3 "$TRANSCRIBE_PY" "$@"
  fi
}

echo "Transcribing chunks..." >&2
parts=()
total="${#sorted_chunks[@]}"
idx=0
last=$(( total - 1 ))
for chunk_path in "${sorted_chunks[@]}"; do
  base="$(basename "$chunk_path")"
  echo "Transcribing chunk ${idx}/${last}: ${base}..." >&2
  if ! run_transcribe "$chunk_path" "$model_size" "$model_cache_dir" >> "$output_txt"; then
    echo "Error transcribing ${base}" >&2
    exit 1
  fi
  idx=$((idx + 1))
done

echo "Transcript written to $output_txt" >&2
echo "Done." >&2
