#!/usr/bin/env python3
"""
Video Analysis Tool - Three-Tier Approach
Combines Whisper (transcription) + PySceneDetect (scene detection) + Gemini (visual analysis)
to generate an edit list matching script to video footage.
"""

import sys
import os
import json
import argparse
from pathlib import Path
import subprocess

def transcribe_with_whisper(video_path, model_size="base"):
    """
    Transcribe video audio using Whisper.

    Args:
        video_path: Path to video file
        model_size: Whisper model (tiny, base, small, medium, large)
                   base = good quality, fast (74MB)
                   small = better quality, slower (244MB)

    Returns:
        dict with segments containing timestamps and text
    """
    import whisper

    print(f"\n[1/3] Transcribing audio with Whisper ({model_size} model)...")

    model = whisper.load_model(model_size)
    result = model.transcribe(str(video_path))

    print(f"✓ Transcribed {len(result['segments'])} segments")

    return result

def detect_scenes(video_path, threshold=27.0):
    """
    Detect scene changes using PySceneDetect.

    Args:
        video_path: Path to video file
        threshold: Sensitivity (lower = more sensitive, 27 is default)

    Returns:
        list of scene timestamps
    """
    from scenedetect import open_video, SceneManager
    from scenedetect.detectors import ContentDetector

    print(f"\n[2/3] Detecting scene changes...")

    video = open_video(str(video_path))
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    print(f"✓ Detected {len(scene_list)} scene changes")

    # Convert to simple timestamp format
    scenes = []
    for i, (start_time, end_time) in enumerate(scene_list):
        scenes.append({
            'scene_number': i + 1,
            'start': start_time.get_seconds(),
            'end': end_time.get_seconds(),
            'duration': (end_time - start_time).get_seconds()
        })

    return scenes

def analyze_with_gemini(video_path, transcript, scenes, script_content=None):
    """
    Upload video to Gemini for visual analysis.

    Args:
        video_path: Path to video file
        transcript: Whisper transcription result
        scenes: PySceneDetect scene list
        script_content: Optional script text to match against

    Returns:
        Gemini's analysis and edit suggestions
    """
    import google.generativeai as genai

    print(f"\n[3/3] Analyzing video content with Gemini 2.0 Flash...")

    # Configure Gemini
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("Get your API key from: https://aistudio.google.com/apikey")
        sys.exit(1)

    genai.configure(api_key=api_key)

    # Upload video
    print(f"Uploading video to Gemini...")
    video_file = genai.upload_file(str(video_path))
    print(f"✓ Uploaded: {video_file.name}")

    # Wait for processing
    import time
    while video_file.state.name == "PROCESSING":
        print("  Processing video...", end='\r')
        time.sleep(2)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError("Video processing failed")

    print("✓ Video ready for analysis")

    # Build analysis prompt
    prompt = f"""Analyze this video and provide a detailed breakdown of its visual content.

TRANSCRIPT (from Whisper):
{json.dumps(transcript['segments'][:5], indent=2)}... (showing first 5 segments)

DETECTED SCENES:
{json.dumps(scenes[:10], indent=2)}... (showing first 10 scenes)

VIDEO FILE: {video_path.name}

"""

    if script_content:
        prompt += f"""
SCRIPT TO MATCH:
{script_content[:2000]}... (showing first 2000 chars)

Please provide:
1. Visual description of each major scene
2. Key moments and what's shown
3. Edit suggestions: which timestamps from this footage would work for specific script sections
4. Recommendations for which clips to use where in the final video
"""
    else:
        prompt += """
Please provide:
1. Visual description of each major scene
2. Key moments and timestamps
3. What text overlays or graphics would work well
4. Suggestions for how to use this footage effectively
"""

    # Analyze with Gemini 2.0 Flash
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content([video_file, prompt])

    print(f"✓ Analysis complete")

    return {
        'video_file': video_file.name,
        'analysis': response.text
    }

def save_results(output_path, transcript, scenes, gemini_analysis):
    """Save all analysis results to a JSON file."""

    results = {
        'transcript': {
            'text': transcript['text'],
            'language': transcript['language'],
            'segments': [
                {
                    'id': seg['id'],
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text']
                }
                for seg in transcript['segments']
            ]
        },
        'scenes': scenes,
        'gemini_analysis': gemini_analysis
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_path}")

    # Also save human-readable version
    txt_path = output_path.with_suffix('.txt')
    with open(txt_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("VIDEO ANALYSIS RESULTS\n")
        f.write("=" * 80 + "\n\n")

        f.write("TRANSCRIPT:\n")
        f.write("-" * 80 + "\n")
        for seg in transcript['segments']:
            f.write(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}\n")

        f.write("\n\nSCENE BREAKDOWN:\n")
        f.write("-" * 80 + "\n")
        for scene in scenes:
            f.write(f"Scene {scene['scene_number']}: {scene['start']:.1f}s - {scene['end']:.1f}s ({scene['duration']:.1f}s)\n")

        f.write("\n\nGEMINI VISUAL ANALYSIS:\n")
        f.write("-" * 80 + "\n")
        f.write(gemini_analysis['analysis'])
        f.write("\n")

    print(f"✓ Human-readable version: {txt_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze video using Whisper + PySceneDetect + Gemini',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Analyze single video
  %(prog)s video.mp4 -o analysis.json

  # Analyze with script matching
  %(prog)s video.mp4 -o analysis.json -s script.md

  # Use better Whisper model (slower, more accurate)
  %(prog)s video.mp4 -o analysis.json --whisper-model small

  # Batch analyze all videos in folder
  %(prog)s videos/*.mp4 -d ./analysis/
        '''
    )

    parser.add_argument('videos', nargs='+', help='Video file(s) to analyze')
    parser.add_argument('-o', '--output', help='Output file (for single video)')
    parser.add_argument('-d', '--output-dir', help='Output directory (for batch mode)')
    parser.add_argument('-s', '--script', help='Script file to match against')
    parser.add_argument('--whisper-model', default='base',
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper model size (default: base)')
    parser.add_argument('--scene-threshold', type=float, default=27.0,
                       help='Scene detection sensitivity (default: 27.0)')

    args = parser.parse_args()

    # Load script if provided
    script_content = None
    if args.script:
        script_path = Path(args.script)
        if script_path.exists():
            script_content = script_path.read_text()
            print(f"Loaded script: {script_path} ({len(script_content)} chars)")
        else:
            print(f"Warning: Script file not found: {script_path}")

    # Determine output mode
    if len(args.videos) == 1 and args.output:
        # Single video mode
        video_path = Path(args.videos[0])
        output_path = Path(args.output)
    elif args.output_dir:
        # Batch mode
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        parser.error("Use -o for single video or -d for batch mode")

    # Process videos
    for video_file in args.videos:
        video_path = Path(video_file)

        if not video_path.exists():
            print(f"ERROR: Video not found: {video_path}")
            continue

        print(f"\n{'='*80}")
        print(f"ANALYZING: {video_path.name}")
        print(f"{'='*80}")

        # Step 1: Transcribe with Whisper
        transcript = transcribe_with_whisper(video_path, args.whisper_model)

        # Step 2: Detect scenes
        scenes = detect_scenes(video_path, args.scene_threshold)

        # Step 3: Analyze with Gemini
        gemini_analysis = analyze_with_gemini(
            video_path,
            transcript,
            scenes,
            script_content
        )

        # Save results
        if args.output_dir:
            output_path = Path(args.output_dir) / f"{video_path.stem}-analysis.json"

        save_results(output_path, transcript, scenes, gemini_analysis)

    print(f"\n{'='*80}")
    print("✓ ALL VIDEOS ANALYZED SUCCESSFULLY")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
