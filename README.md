# Audio Transcription with Speaker Detection

A Python-based tool that uses AssemblyAI's Lemur for accurate audio transcription with speaker detection. The tool provides high-quality transcription and speaker identification using AssemblyAI's advanced AI models.

## Features

- Multi-speaker detection and diarization
- High-accuracy transcription using AssemblyAI's Lemur
- Automatic language detection
- Detailed output with timestamps and speaker labels
- Simple and efficient processing
- No audio chunking needed - handles files of any length

## Requirements

- Python 3.8+
- AssemblyAI API key

## Installation

1. Install dependencies using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the root directory
2. Add your API key:

```plaintext
ASSEMBLYAI_API_KEY=your-assemblyai-api-key
```

## Usage

1. Place your audio file in the project directory
2. Update the audio file path in run.py
3. Run the transcription:

```bash
python run.py
```

The script will:

- Upload your audio file to AssemblyAI
- Process the transcription with speaker detection
- Save the results to a JSON file

## Output Format

The tool generates a JSON file containing:

```json
{
  "metadata": {
    "processed_at": "timestamp",
    "filename": "input_file.mp3",
    "total_speakers": "number of speakers detected"
  },
  "segments": [
    {
      "text": "transcribed text",
      "start": "start_time in seconds",
      "end": "end_time in seconds",
      "speaker": "Speaker A"
    }
  ],
  "text": "full transcript with speaker labels"
}
```

## Performance

- Efficient processing using AssemblyAI's cloud infrastructure
- No local processing required
- Handles files of any length
- Maintains consistent speaker labels throughout the transcript

## Limitations

- Requires clear audio with minimal background noise
- Best results when speakers have distinct voices
- Each speaker should have sufficient speech samples
- Internet connection required for processing

## Supported Audio Formats

- MP3
- MP4
- WAV
- FLAC
- And many more common audio formats

## Acknowledgments

- [AssemblyAI](https://www.assemblyai.com/) for transcription and speaker detection

## Support

For issues and feature requests, please use the GitHub Issues page.

```

```
