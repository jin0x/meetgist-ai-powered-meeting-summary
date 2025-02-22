Here's the modified README.md without the cloning instructions:

````markdown
# Audio Transcription with Speaker Detection

A Python-based tool that combines OpenAI's Whisper and AssemblyAI for accurate audio transcription with speaker detection. The tool processes audio files in parallel, providing both transcription and speaker identification.

## Features

- Multi-speaker detection
- Parallel processing for faster transcription
- Support for long audio files through chunking
- High-accuracy transcription using OpenAI's Whisper
- Speaker diarization using AssemblyAI
- Detailed output with timestamps and speaker labels

## Requirements

- Python 3.8+
- OpenAI API key
- AssemblyAI API key

## Installation

1. Install dependencies using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```
````

## Configuration

1. Create a `.env` file in the root directory
2. Add your API keys:

```python
OPENAI_API_KEY = "your-openai-api-key"
ASSEMBLYAI_API_KEY = "your-assemblyai-api-key"
```

## Usage

1. Place your audio file in the project directory
2. Run the transcription:

```bash
python run.py
```

The script will:

- Split the audio into manageable chunks
- Process transcription and speaker detection in parallel
- Combine results into a single output file

## Output Format

The tool generates a JSON file containing:

```json
{
    "metadata": {
        "processed_at": "timestamp",
        "filename": "input_file.mp3",
        "processing_time": "duration in seconds",
        "total_speakers": "number of speakers detected"
    },
    "segments": [
        {
            "text": "transcribed text",
            "start": start_time,
            "end": end_time,
            "speaker": "Speaker 1",
            "confidence": confidence_score
        }
        // ... more segments
    ],
    "text": "full transcript with speaker labels"
}
```

## Performance

- Processes audio files in parallel for improved speed
- Handles files of any length through efficient chunking
- Maintains speaker consistency across chunks
- Optimizes audio for better speaker detection

## Limitations

- Requires clear audio with minimal background noise
- Best results when speakers have distinct voices
- Each speaker should have at least 30 seconds of speech
- Maximum of 10 speakers per audio file

## Acknowledgments

- [OpenAI Whisper](https://openai.com/research/whisper) for transcription
- [AssemblyAI](https://www.assemblyai.com/) for speaker detection
- [pydub](https://github.com/jiaaro/pydub) for audio processing

## Support

For issues and feature requests, please use the GitHub Issues page.

```

```
