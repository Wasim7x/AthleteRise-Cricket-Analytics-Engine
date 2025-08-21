import os
import cv2
import sys
import pathlib
import yt_dlp

sys.path[0] = str(pathlib.Path(__file__).parent.parent.resolve())

class VideoProcessor:
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = config['output']['directory']
        self.video_url = config['input_video']['url']
        if self.video_url == "NONE":
            print("No video URL provided in configuration. Please update the config.yaml file.")
            return
        os.makedirs(self.output_dir, exist_ok=True)


    def download_video(self, output_path: str = './data/') -> str:
        """Download video from YouTube"""
        os.makedirs(output_path, exist_ok=True)
        
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.video_url, download=True)
            filename = ydl.prepare_filename(info)
            return filename        
        