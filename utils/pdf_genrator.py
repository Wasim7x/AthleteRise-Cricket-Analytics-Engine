#!/usr/bin/env python3
"""
Simple JSON to PDF Converter for Cricket Analysis (FIXED VERSION)
Converts evaluation.json to a professional PDF report
"""

from fpdf import FPDF
import json
import os
from datetime import datetime, timedelta
import sys

class SimpleCricketPDF(FPDF):
    def header(self):
        """PDF header"""
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 51, 102)  # Dark blue
        self.cell(0, 15, 'Cricket Cover Drive Analysis Report', 0, 1, 'C')
        
        # Add line under header
        self.set_draw_color(0, 51, 102)
        self.set_line_width(0.8)
        self.line(20, 25, 190, 25)
        self.ln(10)
        
    def footer(self):
        """PDF footer"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        
        # Date and page
        date_str = datetime.now().strftime("%B %d, %Y")
        self.cell(0, 10, f'Generated on {date_str} - Page {self.page_no()}', 0, 0, 'C')
        
    def add_section_title(self, title):
        """Add section title"""
        self.ln(5)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, 0, 1, 'L')
        
        # Underline
        self.set_draw_color(0, 51, 102)
        self.line(20, self.get_y()-2, 20 + self.get_string_width(title), self.get_y()-2)
        self.set_text_color(0, 0, 0)
        self.ln(3)
        
    def add_text(self, text, font_size=11, bold=False):
        """Add regular text with unicode character replacement"""
        # Replace problematic unicode characters with ASCII alternatives
        clean_text = text.replace('\u2022', '-')  # Replace bullet with dash
        clean_text = clean_text.replace('\u2713', 'V')  # Replace checkmark with V
        clean_text = clean_text.replace('\u2714', 'V')  # Replace heavy checkmark with V
        clean_text = clean_text.replace('\u00b7', '*')  # Replace middle dot with asterisk
        
        font_style = 'B' if bold else ''
        self.set_font('Arial', font_style, font_size)
        self.multi_cell(0, 6, clean_text)
        self.ln(2)
        
    def add_score_table(self, category_scores):
        """Add category scores table"""
        self.set_font('Arial', 'B', 11)
        
        # Table header
        self.set_fill_color(230, 240, 255)  # Light blue
        self.cell(80, 10, 'Category', 1, 0, 'L', True)
        self.cell(30, 10, 'Score', 1, 0, 'C', True)
        self.cell(70, 10, 'Performance Level', 1, 1, 'C', True)
        
        # Table rows
        self.set_font('Arial', '', 10)
        for category, score in category_scores.items():
            # Category name
            category_name = category.replace('_', ' ').title()
            self.cell(80, 8, category_name, 1, 0, 'L')
            
            # Score
            self.cell(30, 8, f'{score}/10', 1, 0, 'C')
            
            # Performance level with color coding
            level = self.get_performance_level(score)
            color = self.get_level_color(level)
            
            self.set_fill_color(*color)
            self.cell(70, 8, level, 1, 1, 'C', True)
            self.set_fill_color(255, 255, 255)  # Reset to white
            
        self.ln(5)
        
    def get_performance_level(self, score):
        """Get performance level from score"""
        if score >= 8.0:
            return "Excellent"
        elif score >= 6.5:
            return "Good"
        elif score >= 5.0:
            return "Average"
        elif score >= 3.5:
            return "Needs Work"
        else:
            return "Poor"
            
    def get_level_color(self, level):
        """Get color for performance level"""
        colors = {
            "Excellent": (144, 238, 144),    # Light green
            "Good": (173, 216, 230),         # Light blue
            "Average": (255, 255, 224),      # Light yellow
            "Needs Work": (255, 218, 185),   # Light orange
            "Poor": (255, 182, 193)          # Light red
        }
        return colors.get(level, (255, 255, 255))
        
    def add_overall_score_box(self, overall_score, grade):
        """Add highlighted overall score box"""
        self.ln(5)
        
        # Box dimensions
        box_width = 160
        box_height = 30
        box_x = (210 - box_width) / 2  # Center the box
        box_y = self.get_y()
        
        # Box background color based on score
        if overall_score >= 7.0:
            bg_color = (144, 238, 144)  # Green
        elif overall_score >= 5.0:
            bg_color = (255, 255, 224)  # Yellow
        else:
            bg_color = (255, 182, 193)  # Red
            
        self.set_fill_color(*bg_color)
        self.rect(box_x, box_y, box_width, box_height, 'F')
        
        # Box border
        self.set_draw_color(100, 100, 100)
        self.rect(box_x, box_y, box_width, box_height)
        
        # Text inside box
        self.set_y(box_y + 5)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, f'Overall Score: {overall_score}/10', 0, 1, 'C')
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, f'Performance Grade: {grade}', 0, 1, 'C')
        
        self.set_y(box_y + box_height + 10)

def generate_simple_pdf_report(json_file_path, output_dir="./output"):
    """
    Generate PDF report from JSON evaluation file
    
    Args:
        json_file_path: Path to the JSON evaluation file
        output_dir: Directory to save the PDF
    """
    
    # Load JSON data
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: JSON file not found: {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file: {json_file_path}")
        return None
    
    # Extract data
    overall_score = data.get('overall_score', 0)
    category_scores = data.get('category_scores', {})
    feedback = data.get('feedback', {})
    grade = data.get('grade', 'Unknown')
    
    # Create PDF
    pdf = SimpleCricketPDF()
    pdf.add_page()
    
    # Title section
    pdf.ln(10)
    pdf.add_overall_score_box(overall_score, grade)
    
    # Performance summary
    pdf.add_section_title("Performance Summary")
    
    summary_text = f"""
This report analyzes cricket cover drive technique across five key biomechanical categories. 
The overall performance score of {overall_score}/10 indicates a {grade.lower()} level of 
technical execution requiring focused improvement in fundamental areas.

Analysis Date: {datetime.now().strftime("%B %d, %Y")}
Performance Grade: {grade}
    """
    pdf.add_text(summary_text.strip())
    
    # Category breakdown
    pdf.add_section_title("Category Performance Breakdown")
    pdf.add_score_table(category_scores)
    
    # Detailed feedback
    pdf.add_section_title("Detailed Technical Feedback")
    
    for category, feedback_list in feedback.items():
        category_name = category.replace('_', ' ').title()
        score = category_scores.get(category, 0)
        
        pdf.add_text(f"{category_name} (Score: {score}/10):", font_size=12, bold=True)
        
        for i, feedback_item in enumerate(feedback_list, 1):
            pdf.add_text(f"  {i}. {feedback_item}", font_size=10)
        
        pdf.ln(3)
    
    # Training recommendations
    pdf.add_section_title("Training Recommendations")
    
    if overall_score < 4.0:
        recommendations = [
            "Focus on fundamental technique development with qualified coaching",
            "Practice basic stance and grip positioning daily",
            "Work on balance and footwork through repetitive drills",
            "Use mirror practice for visual feedback on body positioning",
            "Start with stationary ball practice before moving deliveries"
        ]
    elif overall_score < 6.0:
        recommendations = [
            "Continue working on identified weak areas with consistent practice",
            "Incorporate video analysis to compare with professional technique",
            "Focus on timing and rhythm development",
            "Practice weight transfer and follow-through completion",
            "Gradually increase ball pace while maintaining form"
        ]
    else:
        recommendations = [
            "Maintain current technique while fine-tuning minor adjustments",
            "Focus on consistency across different ball types and conditions",
            "Work on advanced shot variations and adaptations",
            "Incorporate match simulation practice scenarios"
        ]
    
    for i, rec in enumerate(recommendations, 1):
        pdf.add_text(f"{i}. {rec}")
    
    # Practice schedule - FIXED to use ASCII characters only
    pdf.add_section_title("Recommended Practice Schedule")
    
    schedule_text = """
Week 1-2: Foundation Building
- 20 minutes daily: Basic stance, grip, and balance work
- 30 minutes: Slow-motion practice focusing on identified weak areas
- 15 minutes: Shadow batting without ball for muscle memory

Week 3-4: Skill Integration
- 25 minutes: Practice with slow deliveries maintaining correct form
- 20 minutes: Focus specifically on lowest-scoring categories
- 15 minutes: Video review and technique comparison

Week 5+: Progressive Development
- 30 minutes: Gradual increase in ball pace while maintaining technique
- 20 minutes: Consistency challenges and repetition drills
- 10 minutes: Performance tracking and progress assessment
    """
    
    pdf.add_text(schedule_text.strip())
    
    # Progress tracking - FIXED DATE CALCULATION
    pdf.add_section_title("Progress Tracking")
    
    # Calculate next evaluation date correctly
    next_eval_date = (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")
    
    # Create safe category list for priority areas
    priority_categories = [cat.replace('_', ' ').title() for cat, score in category_scores.items() if score < 4]
    priority_text = ', '.join(priority_categories) if priority_categories else "All categories need attention"
    
    tracking_text = f"""
To monitor improvement, focus on these key metrics:

- Target overall score improvement: Aim for {min(10, overall_score + 2)}/10 within 4 weeks
- Priority categories: {priority_text}
- Record weekly practice sessions for technique comparison
- Re-analyze technique monthly using the same evaluation criteria

Next evaluation recommended: {next_eval_date}
    """
    
    pdf.add_text(tracking_text.strip())
    
    # Save PDF
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f'cricket_analysis_report_{timestamp}.pdf')
    
    try:
        pdf.output(output_path)
        return output_path
    except Exception as e:
        print(f"Error saving PDF: {e}")
        return None

def main():
    """Main function - can be run with command line arguments or interactively"""
    
    # Check for command line argument
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        # Interactive mode - look for JSON files in output directory
        output_dir = "./output"
        if os.path.exists(output_dir):
            json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            
            if not json_files:
                print("No JSON files found in ./output/ directory")
                json_file = input("Enter path to JSON file: ").strip()
            elif len(json_files) == 1:
                json_file = os.path.join(output_dir, json_files)
                print(f"Found JSON file: {json_files}")
            else:
                print("Multiple JSON files found:")
                for i, file in enumerate(json_files, 1):
                    print(f"{i}. {file}")
                
                try:
                    choice = int(input("Select file number: ")) - 1
                    json_file = os.path.join(output_dir, json_files[choice])
                except (ValueError, IndexError):
                    print("Invalid selection")
                    return
        else:
            json_file = input("Enter path to JSON file: ").strip()
    
    # Generate PDF
    print(f"Generating PDF report from {json_file}...")
    
    pdf_path = generate_simple_pdf_report(json_file)
    
    if pdf_path:
        print(f"✅ PDF report generated successfully!")
        print(f"Saved as: {pdf_path}")
        print(f"File size: {os.path.getsize(pdf_path)} bytes")
    else:
        print("❌ Failed to generate PDF report")

if __name__ == "__main__":
    main()
