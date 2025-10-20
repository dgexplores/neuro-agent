#!/usr/bin/env python3
"""
Generate Project Media images for AWS AI Agent Global Hackathon submission
- Extract key frames from demo video
- Capture screenshots from live website
- Resize to 3:2 ratio (optimal: 1200x800px)
- Output: JPG format, <5MB each
"""

import subprocess
import os
from playwright.sync_api import sync_playwright
from PIL import Image

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "images")
DEMO_VIDEO = os.path.join(SCRIPT_DIR, "..", "demo_video", "output", "NeuroAgent_Demo_Final.mp4")
FFMPEG = os.path.join(SCRIPT_DIR, "..", "demo_video", "ffmpeg", "bin", "ffmpeg.exe")

# URLs
FRONTEND_URL = "https://neuro-agent-inipnfo7p-thc1006s-projects.vercel.app/"
API_DOCS_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/docs"
GITHUB_URL = "https://github.com/thc1006/neuro-agent"

# Target dimensions (3:2 ratio)
TARGET_WIDTH = 1200
TARGET_HEIGHT = 800

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_video_frame(timestamp: str, output_filename: str):
    """Extract frame from demo video at specific timestamp"""
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    # Check if FFmpeg exists
    if not os.path.exists(FFMPEG):
        print(f"Warning: FFmpeg not found at {FFMPEG}")
        print("Skipping video frame extraction")
        return False

    cmd = [
        FFMPEG,
        "-ss", timestamp,  # Seek to timestamp
        "-i", DEMO_VIDEO,   # Input video
        "-vframes", "1",    # Extract 1 frame
        "-vf", f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
        "-q:v", "2",        # High quality JPEG
        "-y",               # Overwrite
        output_path
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"OK: Extracted frame at {timestamp} -> {output_filename}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to extract frame: {e}")
        return False

def capture_screenshot(url: str, output_filename: str, wait_time: int = 3):
    """Capture screenshot from live website"""
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.goto(url)
            page.wait_for_timeout(wait_time * 1000)

            # Take screenshot
            page.screenshot(path=output_path + ".tmp.png", full_page=False)
            browser.close()

        # Resize to 3:2 ratio
        resize_to_3x2(output_path + ".tmp.png", output_path)
        os.remove(output_path + ".tmp.png")

        print(f"OK: Captured screenshot from {url} -> {output_filename}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to capture screenshot: {e}")
        return False

def resize_to_3x2(input_path: str, output_path: str):
    """Resize image to 3:2 ratio (1200x800)"""
    img = Image.open(input_path)

    # Calculate crop dimensions for 3:2 ratio
    width, height = img.size
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT  # 1.5
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Image is too wide, crop width
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    else:
        # Image is too tall, crop height
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))

    # Resize to target dimensions
    img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)

    # Save as high-quality JPEG
    img.convert("RGB").save(output_path, "JPEG", quality=95, optimize=True)

    # Check file size
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Image size: {file_size_mb:.2f} MB")

def main():
    print("=" * 60)
    print("Generating Project Media Images")
    print("Target: 3:2 ratio (1200x800px), JPEG, <5MB")
    print("=" * 60)

    # 1. Extract key frames from demo video
    print("\n[1/6] Extracting intro card from demo video...")
    extract_video_frame("00:00:01.5", "1_intro_card.jpg")

    print("\n[2/6] Extracting diagnosis demo from video...")
    extract_video_frame("00:01:25", "2_diagnosis_demo.jpg")

    print("\n[3/6] Extracting architecture from video...")
    extract_video_frame("00:02:50", "3_architecture.jpg")

    # 2. Capture live screenshots
    print("\n[4/6] Capturing frontend homepage...")
    capture_screenshot(FRONTEND_URL, "4_frontend_homepage.jpg")

    print("\n[5/6] Capturing API documentation...")
    capture_screenshot(API_DOCS_URL, "REDACTED")

    print("\n[6/6] Capturing GitHub repository...")
    capture_screenshot(GITHUB_URL, "6_github_repo.jpg")

    print("\n" + "=" * 60)
    print("Project Media Generation Complete!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)

    # List generated files
    print("\nGenerated files:")
    for filename in sorted(os.listdir(OUTPUT_DIR)):
        if filename.endswith(".jpg"):
            filepath = os.path.join(OUTPUT_DIR, filename)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  - {filename} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
