import os
import sys
import pathlib

from utils.config_reader import ConfigReader
from utils.logging import setup_logger
from src.video_processor import VideoProcessor


def main():

    logger = setup_logger()

    logger.info("Program started")
    config_path = r"configs\\confi.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    config = ConfigReader.load_config(config_path)
    logger.info("Configuration loaded successfully")

    video_processor = VideoProcessor(config)
    data_dir = video_processor.download_video()
    logger.info(f"Video downloaded to: {data_dir}")
    


if __name__ == "__main__":
    main()
    