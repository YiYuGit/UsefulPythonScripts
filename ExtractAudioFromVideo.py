# This script extract audo from input mp4 video

import sys
from moviepy.editor import *

def extract_audio(input_file, output_file):
    try:
        # Load the input MP4 file
        video_clip = VideoFileClip(input_file)

        # Extract the audio
        audio_clip = video_clip.audio
        
        audio_clip.write_audiofile(output_file)



        print("Audio extraction successful!")
    except Exception as e:
        print(f"Audio extraction failed: {str(e)}")

if __name__ == "__main__":
    input_file = "C:\SoundExtract\test.mp4"  # Replace with your input file path
    output_file = "C:\SoundExtract\test.mp3"  # Replace with your desired output file path

    extract_audio(input_file, output_file)
