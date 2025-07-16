#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from datetime import datetime
import base64

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 環境変数読み込み
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

# Initialize Google Gemini
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    print('❌ GOOGLE_API_KEY not found in .env file')
    exit(1)

genai.configure(api_key=google_api_key)

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
    # Try different model approaches
    model_variants = [
        'imagen-3.0-generate-001',
        'imagen-3.0-fast-generate-001', 
        'imagegeneration@006'
    ]
    
    for model_name in model_variants:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            response = model.generate_content([
                chapter_prompt,
                {
                    "mime_type": "image/jpeg",
                    "aspect_ratio": "16:9"
                }
            ])
            
            if response.parts:
                print(f"✅ Generated with {model_name}")
                # Process response...
                break
                
        except Exception as model_error:
            print(f"Model {model_name} failed: {model_error}")
            continue
    else:
        print("❌ All models failed")

except Exception as e:
    print(f'❌ Error: {e}')
    
    # Fallback: Use existing script approach
    print("🔄 Trying fallback method...")
    
    # Create a simple prompt file and use existing image generator
    chapter4_info = {
        'title': '第4章：感謝の非対称性―一方通行の優しさが持つ意外な価値',
        'theme': 'philosophical gratitude, one-way appreciation, internal value',
        'number': '4'
    }
    
    simple_prompt = f"""A serene person at a computer expressing gratitude, surrounded by warm golden light. Crystal number "4" on desk. Philosophical atmosphere with warm amber colors. No text visible."""
    
    # Save manually generated image info
    output_dir = Path('outputs/なぜ我々はAIに「ありがとう」と言ってしまうのか？生成AIと人間の奇妙な心理的共生関係-INT-01')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    prompt_file = output_dir / 'chapter4_prompt.txt'
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(f"Chapter 4 Thumbnail Prompt:\n{simple_prompt}\n\nGenerated: {datetime.now()}")
    
    print(f"✅ Prompt saved for manual generation: {prompt_file}")
    print("ℹ️  Please use this prompt with an available image generation service")