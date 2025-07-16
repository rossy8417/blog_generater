#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 環境変数読み込み
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

# Initialize Google Gemini for Imagen 3
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    print('❌ GOOGLE_API_KEY not found in .env file')
    exit(1)

google_client = genai.Client(api_key=google_api_key)

# Chapter 4 content analysis
chapter_prompt = """A peaceful, contemplative scene showing a person sitting at a desk with a computer, expressing gratitude with gentle, serene facial expression. The person has their hands positioned in a thankful gesture toward the screen. Warm golden light emanates from around the person, flowing outward in soft waves, symbolizing the internal value and beauty of one-way gratitude.

The number "4" is creatively integrated as an elegant, translucent crystal sculpture on the desk, catching and refracting the warm light beautifully. 

The background features abstract elements representing the flow of unreciprocated appreciation: delicate streams of light, geometric shapes moving in one direction, and gentle particle effects that flow from the person outward. 

The environment is cozy and philosophical: books, a warm cup of tea, soft furnishings, creating an atmosphere of peaceful contemplation and inner warmth.

Style: Digital illustration with warm, philosophical atmosphere
Color palette: Warm golds, amber tones, soft orange, peaceful whites
Mood: Contemplative, spiritually uplifting, serene
No text or written words visible anywhere in the image.
Aspect ratio: 16:9 landscape format"""

print("🎨 Generating Chapter 4 thumbnail with Google Imagen 3...")

try:
    # Generate image using Imagen 3
    response = google_client.models.generate_image(
        model='imagen-3.0-generate-001',
        prompt=chapter_prompt,
        config=types.GenerateImageConfig(
            aspect_ratio='16:9',
            negative_prompt='text, words, letters, numbers written on image, speech bubbles, signs',
            safety_filter_level='BLOCK_ONLY_HIGH',
            person_generation='ALLOW_ADULT'
        )
    )
    
    # Save the generated image
    if response.images:
        image_data = response.images[0]._image_bytes
        
        # Create output directory
        output_dir = Path('outputs/なぜ我々はAIに「ありがとう」と言ってしまうのか？生成AIと人間の奇妙な心理的共生関係-INT-01')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{timestamp}_thumbnail_chapter4.jpg'
        filepath = output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        print(f'✅ Chapter 4 thumbnail saved: {filepath}')
        print(f'📁 File size: {len(image_data) / 1024:.1f} KB')
        
    else:
        print('❌ No image generated in response')
        
except Exception as e:
    print(f'❌ Error generating image: {e}')
    print('Error details:', str(e))