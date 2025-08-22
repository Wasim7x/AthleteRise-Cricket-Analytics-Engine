import cv2
import os
import time
import yaml
from typing import Dict, List
from tqdm import tqdm
from src.pose_estimator import PoseEstimator
from src.biomechanics import BiomechanicsAnalyzer
from src.video_processor import VideoProcessor
from src.evaluator import ShotEvaluator
from utils.config_reader import ConfigReader
from utils.logging import setup_logger
from utils.pdf_genrator import generate_simple_pdf_report
logger = setup_logger()



def analyze_video(video_path: str, config_path: str = "configs\\config.yaml") -> Dict:
    """
    Main function to analyze cricket cover drive video
    
    Args:
        video_path: Path to input video file
        config_path: Path to configuration file
        
    Returns:
        Dictionary containing analysis results
    """
    
    # Load configuration
    config_reader = ConfigReader()
    config = config_reader.load_config(config_path)
    
    # Initialize components
    pose_estimator = PoseEstimator(config)
    logger.info("Pose Estimator initialized")
    biomechanics = BiomechanicsAnalyzer(config)
    logger.info("Biomechanics Analyzer initialized")
    video_processor = VideoProcessor(config)
    logger.info("Video Processor initialized")
    evaluator = ShotEvaluator(config)
    logger.info("Shot Evaluator initialized")
    
    # Setup paths
    output_dir = config['output']['directory']
    os.makedirs(output_dir, exist_ok=True)
    output_video_path = os.path.join(output_dir, config['output']['video_name'])
    evaluation_path = os.path.join(output_dir, config['output']['evaluation_file'])
    
    # Open input video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Setup video writer
    writer, video_info = video_processor.setup_video_writer(video_path, output_video_path)
    
    # Initialize tracking variables
    metrics_history = []
    frame_count = 0

    
    print(f"Processing input video having {video_info['total_frames']} frames is FPS is {video_info['fps']}...")
    
    # Process video frame by frame
    with tqdm(total=video_info['total_frames'], desc="Processing frames") as pbar:
        start_time = time.time()
        total_time = 0
        frames_processing_time = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_start_time = time.time()
          
            # Resize frame if neededvideo_info
            if (frame.shape[1] != video_info['target_width'] or 
                frame.shape[0] != video_info['target_height']):
                frame = cv2.resize(frame, (video_info['target_width'], 
                                            video_info['target_height']))
            
            # Extract pose
            pose_data = pose_estimator.extract_keypoints(frame)
            
            # Initialize frame metrics
            frame_metrics = {
                'frame_number': frame_count,
                'elbow_angle': None,
                'spine_lean': None,
                'head_knee_distance': None,
                'foot_direction': None
            }
            
            if pose_data:
                landmarks = pose_data['landmarks']
                frame_shape = frame.shape
                
                # Calculate biomechanical metrics
                elbow_angle = biomechanics.calculate_front_elbow_angle(
                    landmarks, frame_shape, pose_estimator)
                spine_lean = biomechanics.calculate_spine_lean(
                    landmarks, frame_shape, pose_estimator)
                head_knee_distance = biomechanics.calculate_head_knee_alignment(
                    landmarks, frame_shape, pose_estimator)
                foot_direction = biomechanics.calculate_foot_direction(
                    landmarks, frame_shape, pose_estimator)
                
                # Update frame metrics
                if elbow_angle: frame_metrics['elbow_angle'] = elbow_angle
                if spine_lean: frame_metrics['spine_lean'] = spine_lean
                if head_knee_distance: frame_metrics['head_knee_distance'] = head_knee_distance
                if foot_direction: frame_metrics['foot_direction'] = foot_direction
                
                # Draw pose skeleton
                frame = pose_estimator.draw_pose(frame, pose_data)
                
                # Get real-time feedback
                feedback = biomechanics.evaluate_metrics(frame_metrics)
                
                # Add overlays
                frame = video_processor.add_metrics_overlay(frame, frame_metrics, feedback)
            
            # Store metrics for final evaluation
            metrics_history.append(frame_metrics)

            cv2.imshow('pose_estimator_output', frame)
  
            frame_count += 1
            current_time = time.time()
            total_time += current_time - frame_start_time
            frames_processing_time += current_time - frame_start_time

            if frame_count % 10 == 0:
                processing_fps = 10 / frames_processing_time if frames_processing_time > 0 else 0
                frames_processing_time = 0
                # Update tqdm bar with FPS info
                pbar.set_postfix(FPS=f"{processing_fps:.2f}")

            # Write frame to output video
            writer.write(frame)

            if video_info['forced_sleep']:
                time.sleep(video_info['forced_sleep'])
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            pbar.update(1)
        
    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    writer.release()

    # avg_fps = frame_count / (time.time()-start_time)
    avg_fps = frame_count / total_time if total_time > 0 else 0
    print(f"\nProcessing complete: {frame_count} frames processed in {total_time:.2f} seconds at average of {avg_fps:.2f} FPS")

    # Calculate final evaluation
    print("Calculating final evaluation...")
    category_scores = evaluator.calculate_category_scores(metrics_history)
    feedback = evaluator.generate_feedback(category_scores)
    
    # Save evaluation
    evaluator.save_evaluation(category_scores, feedback, evaluation_path)

    
    results = {
        'video_info': video_info,
        'processing_fps': avg_fps,
        'output_video': output_video_path,
        'evaluation_file': evaluation_path,
        'category_scores': category_scores,
        'overall_score': evaluator.calculate_overall_score(category_scores),
        'feedback': feedback
    }
    
    return results


def main():

    logger.info("Program started")
    config_path = r"configs\\config.yaml"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    config = ConfigReader.load_config(config_path)
    logger.info("Configuration loaded successfully")

    video_processor = VideoProcessor(config)
    video_path = video_processor.download_video()
    logger.info(f"Video downloaded to: {video_path}")

    # Analyze video
    try:
        print("\nStarting analysis...")
        results = analyze_video(video_path)
        
        # Display results
        print("\n" + "="*50)
        print("ANALYSIS COMPLETE")
        print("="*50)
        print(f"Overall Score: {results['overall_score']}/10")
        print(f"Processing Speed: {results['processing_fps']:.2f} FPS")
        print(f"Output Video: {results['output_video']}")
        print(f"Evaluation File: {results['evaluation_file']}")
        
        print("\nCategory Scores:")
        for category, score in results['category_scores'].items():
            print(f"  {category.replace('_', ' ').title()}: {score}/10")
        
        print("\nDetailed feedback saved to evaluation file.")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error during analysis: {e}")

    # Generate PDF report
    try:
        output_dir = config['output']['directory']
        evaluation_path = os.path.join(output_dir, config['output']['evaluation_file'])   
        pdf_path = generate_simple_pdf_report(evaluation_path) 
        if pdf_path:
            print(f"PDF report generated at: {pdf_path}")
            logger.info(f"PDF report generated at: {pdf_path}") 
        else:
            print("❌ Failed to generate PDF report")  

    except Exception as e:
        print(f"Error generating PDF report: {e}")
        logger.error(f"Error generating PDF report: {e}")                         

if __name__ == "__main__":
    main()
    