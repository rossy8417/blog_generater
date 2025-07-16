import requests
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print('❌ GOOGLE_API_KEY not found in .env file')
    exit(1)

# Try the newest Imagen API endpoint
url = f'https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImage?key={GOOGLE_API_KEY}'

prompt = '''A peaceful scene showing a person sitting at a computer with a gentle, grateful expression. Warm golden light radiates around them. The number 4 appears as a glowing crystal sculpture nearby. Philosophical atmosphere with warm amber colors. No text visible.'''

data = {
    'prompt': prompt,
    'generationConfig': {
        'aspectRatio': '16:9'
    }
}

headers = {'Content-Type': 'application/json'}

print('🎨 Testing Imagen 3 API endpoint...')
response = requests.post(url, headers=headers, data=json.dumps(data))

print(f'Status: {response.status_code}')
if response.status_code != 200:
    print('Response:', response.text[:500])
else:
    print('✅ API call successful!')
    result = response.json()
    if 'generatedImages' in result and len(result['generatedImages']) > 0:
        import base64
        image_data = base64.b64decode(result['generatedImages'][0]['bytesBase64Encoded'])
        
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
        print('Response keys:', list(result.keys()) if 'result' in locals() else 'No result')