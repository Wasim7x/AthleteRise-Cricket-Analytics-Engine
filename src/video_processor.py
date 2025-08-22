import os
import cv2
import sys
import pathlib
import yt_dlp
from typing import Dict, List, Tuple 

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

    def setup_video_writer(self, input_video_path: str, output_path: str) -> Tuple[cv2.VideoWriter, Dict]:
        """Setup video writer with proper codec and settings"""
        cap = cv2.VideoCapture(input_video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Use target dimensions if specified
        target_width = self.config['video'].get('target_width', width)
        target_width = target_width if target_width is not None else width
        target_height = self.config['video'].get('target_height', height)
        target_height = target_height if target_height is not None else width
        target_fps = self.config['video'].get('target_fps', fps)
        forced_sleep= self.config['video'].get('intensional_sleep', 0.2)
        
        cap.release()
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, target_fps, (target_width, target_height))
        
        video_info = {
            'fps': fps,
            'width': width,
            'height': height,
            'total_frames': total_frames,
            'target_fps': target_fps,
            'target_width': target_width,
            'target_height': target_height,
            'forced_sleep': forced_sleep
        }
        
        return writer, video_info
    
    def add_text_overlay(self, frame: np.ndarray, text: str, position: Tuple[int, int], 
                        color: Tuple[int, int, int] = (255, 255, 255), 
                        font_scale: float = 0.4) -> np.ndarray:
        """Add text overlay to frame"""
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 
                   font_scale, color, 1, cv2.LINE_4)
        return frame
    
    def add_metrics_overlay(self, frame: np.ndarray, metrics: Dict, 
                           feedback: Dict) -> np.ndarray:
        """Add biomechanical metrics overlay to frame"""
        y_offset = 20
        
        # Add metrics
        if metrics.get('elbow_angle'):
            text = f"Elbow: {metrics['elbow_angle']:.1f}°"
            frame = self.add_text_overlay(frame, text, (10, y_offset))
            y_offset += 15
        
        if metrics.get('spine_lean'):
            text = f"Spine Lean: {metrics['spine_lean']:.1f}°"
            frame = self.add_text_overlay(frame, text, (10, y_offset))
            y_offset += 15
        
        if metrics.get('head_knee_distance'):
            text = f"Head-Knee: {metrics['head_knee_distance']:.0f}px"
            frame = self.add_text_overlay(frame, text, (10, y_offset))
            y_offset += 15
        
        # Add feedback
        y_offset += 10
        for key, msg in feedback.items():
            color = (0, 255, 0) if "✅" in msg else (0, 0, 255)
            frame = self.add_text_overlay(frame, msg, (10, y_offset), color, 0.5)
            y_offset += 20
        
        return frame

        