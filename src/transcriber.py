import os
from pathlib import Path
import json
import openai
from datetime import datetime
import time
import requests
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

class AudioTranscriber:
    def __init__(self, openai_key: str, assemblyai_key: str):
        """Initialize the transcriber with API keys"""
        print("Initializing clients...")
        if not openai_key:
            raise ValueError("OpenAI API key is missing!")
        if not assemblyai_key:
            raise ValueError("AssemblyAI API key is missing!")
            
        self.client = openai.OpenAI(api_key=openai_key)
        self.headers = {
            "authorization": assemblyai_key,
            "content-type": "application/json"
        }
        self.upload_url = "https://api.assemblyai.com/v2/upload"
        self.transcript_url = "https://api.assemblyai.com/v2/transcript"
    
    def _split_audio(self, audio_path: str):
        """Split audio file into chunks under 25MB"""
        print("Splitting audio into chunks...")
        
        try:
            audio = AudioSegment.from_file(audio_path)
            chunk_length = 120 * 1000  # 2 minutes in milliseconds
            chunks = []
            
            for i, start in enumerate(range(0, len(audio), chunk_length)):
                chunk = audio[start:start + chunk_length]
                chunk_path = f"chunk_{i}.wav"
                # Export as mono audio to reduce file size
                chunk = chunk.set_channels(1)
                chunk.export(chunk_path, format="wav", parameters=["-ac", "1"])
                
                # Verify chunk size
                size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                print(f"Chunk {i+1}: {size_mb:.1f}MB, {len(chunk)/1000:.1f} seconds")
                chunks.append((chunk_path, start/1000))
                
            if not chunks:
                raise ValueError("No chunks were created from the audio file")
            
            return chunks
            
        except Exception as e:
            print(f"Error splitting audio: {str(e)}")
            # Clean up any partial chunks
            for file in Path().glob("chunk_*.wav"):
                file.unlink()
            raise
    
    def _get_speaker_segments(self, audio_path: str) -> List[Dict[str, Any]]:
        """Get speaker segments using AssemblyAI"""
        print("\nStarting speaker detection with AssemblyAI...")
        
        # Optimize audio for speaker detection
        audio = AudioSegment.from_file(audio_path)
        temp_path = "temp_mono.wav"
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio.export(temp_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
        
        try:
            # Upload file
            with open(temp_path, 'rb') as f:
                upload_response = requests.post(
                    self.upload_url,
                    headers=self.headers,
                    data=f
                )
            
            audio_url = upload_response.json()["upload_url"]
            
            # Start speaker detection
            response = requests.post(
                self.transcript_url,
                headers=self.headers,
                json={
                    "audio_url": audio_url,
                    "speaker_labels": True,
                    "language_code": "en"
                }
            )
            
            transcript_id = response.json()['id']
            polling_url = f"{self.transcript_url}/{transcript_id}"
            
            # Wait for completion
            while True:
                response = requests.get(polling_url, headers=self.headers)
                status = response.json()['status']
                
                if status == 'completed':
                    return response.json()['utterances']
                elif status == 'error':
                    raise Exception(f"Speaker detection failed: {response.json()}")
                
                time.sleep(3)
                
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _process_chunk_whisper(self, chunk_data: tuple) -> List[Dict[str, Any]]:
        """Process a single chunk with Whisper"""
        if not chunk_data:
            print("Warning: Received empty chunk data")
            return []
        
        chunk_path, time_offset = chunk_data
        
        try:
            if not os.path.exists(chunk_path):
                print(f"Warning: Chunk file not found: {chunk_path}")
                return []
            
            with open(chunk_path, 'rb') as audio_file:
                print(f"Processing chunk: {chunk_path}")
                transcript = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    language="en"
                )
                
                # Process segments directly
                segments = []
                for segment in transcript.segments:
                    segments.append({
                        "text": segment.text,
                        "start": segment.start + time_offset,
                        "end": segment.end + time_offset,
                        "confidence": getattr(segment, "confidence", None)
                    })
                
                print(f"Processed {len(segments)} segments from {chunk_path}")
                return segments
            
        except Exception as e:
            print(f"Error processing chunk {chunk_path}: {str(e)}")
            return []
        
        finally:
            if os.path.exists(chunk_path):
                try:
                    os.remove(chunk_path)
                    print(f"Removed chunk file: {chunk_path}")
                except Exception as e:
                    print(f"Error removing chunk file {chunk_path}: {str(e)}")
    
    def _merge_speaker_info(self, segments: List[Dict], speaker_segments: List[Dict]) -> List[Dict]:
        """Merge segment-level transcription with speaker information"""
        for segment in segments:
            segment_mid = (segment["start"] + segment["end"]) / 2
            
            # Find matching speaker segment
            for speaker_seg in speaker_segments:
                seg_start = speaker_seg["start"] / 1000  # Convert to seconds
                seg_end = speaker_seg["end"] / 1000
                
                if seg_start <= segment_mid <= seg_end:
                    segment["speaker"] = f"Speaker {speaker_seg['speaker']}"
                    break
            else:
                segment["speaker"] = "Unknown Speaker"
        
        return segments
    
    def _combine_words_to_segments(self, words: List[Dict]) -> List[Dict]:
        """Combine words into meaningful segments"""
        segments = []
        current_segment = None
        
        for word in words:
            if not current_segment:
                current_segment = {
                    "text": word["text"],
                    "start": word["start"],
                    "end": word["end"],
                    "speaker": word["speaker"]
                }
            elif (word["speaker"] == current_segment["speaker"] and 
                  word["start"] - current_segment["end"] < 0.3):
                # Extend current segment
                current_segment["text"] += " " + word["text"]
                current_segment["end"] = word["end"]
            else:
                # Start new segment
                segments.append(current_segment)
                current_segment = {
                    "text": word["text"],
                    "start": word["start"],
                    "end": word["end"],
                    "speaker": word["speaker"]
                }
        
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def transcribe(self, audio_path: str, output_path: str = None) -> dict:
        """Transcribe audio file with parallel processing"""
        try:
            start_time = time.time()
            
            # Verify input file
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            # Split audio into chunks
            chunks = self._split_audio(audio_path)
            if not chunks:
                raise ValueError("Failed to split audio into chunks")
            
            print(f"Split audio into {len(chunks)} chunks")
            
            # Start parallel processing
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Start speaker detection
                speaker_future = executor.submit(self._get_speaker_segments, audio_path)
                
                # Process chunks with Whisper
                print("Starting transcription...")
                chunk_futures = [
                    executor.submit(self._process_chunk_whisper, chunk)
                    for chunk in chunks
                ]
                
                # Collect all segments
                all_segments = []
                for future in chunk_futures:
                    result = future.result()
                    if result:  # Only add non-empty results
                        all_segments.extend(result)
                
                if not all_segments:
                    raise ValueError("No segments were transcribed from the audio")
                
                # Sort segments by start time
                all_segments.sort(key=lambda x: x["start"])
                
                # Get speaker segments and merge
                print("Waiting for speaker detection...")
                speaker_segments = speaker_future.result()
                if not speaker_segments:
                    print("Warning: No speaker segments detected, using default speaker")
                    speaker_segments = [{
                        "speaker": "1",
                        "start": 0,
                        "end": float('inf') * 1000  # Convert to milliseconds
                    }]
                
                # Merge speaker information
                segments_with_speakers = self._merge_speaker_info(all_segments, speaker_segments)
            
            if not segments_with_speakers:
                raise ValueError("No segments were created from the transcription")
        
            # Prepare result
            result = {
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "filename": Path(audio_path).name,
                    "processing_time": f"{time.time() - start_time:.1f} seconds",
                    "total_speakers": len(set(s["speaker"] for s in segments_with_speakers))
                },
                "segments": segments_with_speakers,
                "text": " ".join(f"{seg['speaker']}: {seg['text']}" for seg in segments_with_speakers)
            }
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\nTranscript saved to {output_path}")
            
            return result
            
        except Exception as e:
            print(f"\nError in transcription: {str(e)}")
            # Clean up any remaining chunks
            for file in Path().glob("chunk_*.wav"):
                file.unlink()
            raise
