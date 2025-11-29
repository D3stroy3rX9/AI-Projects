"""
Audio processing utilities
"""
import base64
import os
import tempfile
import subprocess
from typing import List, Optional
from pathlib import Path
import time


# Create temp directory for audio files
TEMP_DIR = Path(tempfile.gettempdir()) / "audio_translator"
TEMP_DIR.mkdir(exist_ok=True)


def save_audio_chunk(base64_data: str, output_path: Optional[str] = None) -> str:
    """
    Decode base64 audio data and save to file

    Args:
        base64_data: Base64 encoded audio data
        output_path: Optional output path. If None, creates temp file

    Returns:
        Path to saved audio file

    Raises:
        ValueError: If base64 data is invalid
    """
    try:
        # Decode base64 data
        audio_bytes = base64.b64decode(base64_data)

        # Generate output path if not provided
        if output_path is None:
            timestamp = int(time.time() * 1000)
            output_path = str(TEMP_DIR / f"audio_{timestamp}.webm")

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)

        print(f"💾 Saved audio: {output_path} ({len(audio_bytes)} bytes)")
        return output_path

    except Exception as e:
        raise ValueError(f"Failed to save audio chunk: {e}")


def convert_to_wav(
    input_path: str,
    output_path: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1
) -> str:
    """
    Convert audio file to WAV format suitable for Whisper

    Whisper expects:
    - 16kHz sample rate
    - Mono (1 channel)
    - WAV format

    Args:
        input_path: Path to input audio file (any format)
        output_path: Optional output path. If None, creates temp file
        sample_rate: Target sample rate (default: 16000 Hz)
        channels: Number of channels (default: 1 = mono)

    Returns:
        Path to converted WAV file

    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If conversion fails
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Generate output path if not provided
    if output_path is None:
        timestamp = int(time.time() * 1000)
        output_path = str(TEMP_DIR / f"audio_{timestamp}.wav")

    try:
        # Try using ffmpeg first (more reliable)
        try:
            return _convert_with_ffmpeg(input_path, output_path, sample_rate, channels)
        except FileNotFoundError:
            # ffmpeg not found, try pydub
            print("⚠️  ffmpeg not found, trying pydub...")
            return _convert_with_pydub(input_path, output_path, sample_rate, channels)

    except Exception as e:
        raise RuntimeError(f"Failed to convert audio: {e}")


def _convert_with_ffmpeg(
    input_path: str,
    output_path: str,
    sample_rate: int,
    channels: int
) -> str:
    """
    Convert audio using ffmpeg

    Args:
        input_path: Input file path
        output_path: Output file path
        sample_rate: Target sample rate
        channels: Number of channels

    Returns:
        Path to converted file
    """
    # ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_path,           # Input file
        '-ar', str(sample_rate),    # Sample rate
        '-ac', str(channels),        # Channels
        '-y',                        # Overwrite output
        '-loglevel', 'error',        # Only show errors
        output_path
    ]

    # Run ffmpeg
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error: {result.stderr}")

    print(f"🔊 Converted to WAV: {output_path} ({sample_rate}Hz, {channels}ch)")
    return output_path


def _convert_with_pydub(
    input_path: str,
    output_path: str,
    sample_rate: int,
    channels: int
) -> str:
    """
    Convert audio using pydub (fallback if ffmpeg not available)

    Args:
        input_path: Input file path
        output_path: Output file path
        sample_rate: Target sample rate
        channels: Number of channels

    Returns:
        Path to converted file
    """
    try:
        from pydub import AudioSegment

        # Load audio
        audio = AudioSegment.from_file(input_path)

        # Convert to mono if needed
        if channels == 1:
            audio = audio.set_channels(1)

        # Resample
        audio = audio.set_frame_rate(sample_rate)

        # Export as WAV
        audio.export(output_path, format='wav')

        print(f"🔊 Converted to WAV (pydub): {output_path}")
        return output_path

    except ImportError:
        raise RuntimeError(
            "Neither ffmpeg nor pydub available. "
            "Install ffmpeg: https://ffmpeg.org/ "
            "Or install pydub: pip install pydub"
        )


def clean_temp_files(file_paths: List[str]) -> int:
    """
    Delete temporary audio files

    Args:
        file_paths: List of file paths to delete

    Returns:
        Number of files successfully deleted
    """
    deleted_count = 0

    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
                print(f"🗑️  Deleted temp file: {file_path}")
        except Exception as e:
            print(f"⚠️  Failed to delete {file_path}: {e}")

    return deleted_count


def clean_old_temp_files(max_age_seconds: int = 3600) -> int:
    """
    Clean up old temporary audio files

    Args:
        max_age_seconds: Delete files older than this (default: 1 hour)

    Returns:
        Number of files deleted
    """
    deleted_count = 0
    current_time = time.time()

    try:
        for file_path in TEMP_DIR.iterdir():
            if file_path.is_file():
                # Check file age
                file_age = current_time - file_path.stat().st_mtime

                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        print(f"⚠️  Failed to delete old file {file_path}: {e}")

    except Exception as e:
        print(f"⚠️  Error cleaning temp directory: {e}")

    if deleted_count > 0:
        print(f"🗑️  Cleaned {deleted_count} old temp files")

    return deleted_count


def get_audio_duration(file_path: str) -> float:
    """
    Get duration of audio file in seconds

    Args:
        file_path: Path to audio file

    Returns:
        Duration in seconds

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    try:
        # Try using ffprobe (part of ffmpeg)
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return float(result.stdout.strip())

    except:
        pass

    # Fallback: use pydub
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert ms to seconds

    except:
        # If all else fails, return 0
        return 0.0


def validate_audio_file(file_path: str) -> bool:
    """
    Validate that file is a valid audio file

    Args:
        file_path: Path to audio file

    Returns:
        True if valid audio file, False otherwise
    """
    if not os.path.exists(file_path):
        return False

    # Check file size (must be > 0 and < 100MB)
    file_size = os.path.getsize(file_path)
    if file_size == 0 or file_size > 100 * 1024 * 1024:
        return False

    # Check file extension
    valid_extensions = ['.wav', '.mp3', '.webm', '.ogg', '.m4a', '.flac']
    file_ext = Path(file_path).suffix.lower()

    return file_ext in valid_extensions
