#!/usr/bin/env python3
"""
統合画像管理システム - Consolidated Image Manager
新規画像生成、WordPress画像更新、画像バージョン管理を統合

機能:
- 新規画像生成（アイキャッチ・サムネイル）
- WordPress画像更新・差し替え
- 画像バージョン管理
- 画像最適化
- 後方互換性維持

使用方法:
    # 新規画像生成
    python consolidated_image_manager.py generate --outline path/to/outline.md --mode eyecatch
    python consolidated_image_manager.py generate --outline path/to/outline.md --mode all
    
    # WordPress画像更新
    python consolidated_image_manager.py update --post-id 1234 --type eyecatch
    python consolidated_image_manager.py update --post-id 1234 --type chapter --chapter-num 1
    
    # 簡単更新（後方互換性）
    python consolidated_image_manager.py quick-update 1234
    
    # バージョン管理
    python consolidated_image_manager.py version --post-id 1234 --action history
    python consolidated_image_manager.py version --post-id 1234 --action restore --version-id VERSION_ID
"""

import os
import sys
import argparse
import json
import hashlib
import re
import base64
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from io import BytesIO

from google import genai
from google.genai import types
from openai import OpenAI
from PIL import Image, ImageFilter, ImageDraw
from dotenv import load_dotenv
import numpy as np

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.output_manager import OutputManager

# 環境変数読み込み
load_dotenv()


class ImageVersionManager:
    """画像バージョン管理システム"""
    
    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.version_db = {}
        self._load_version_database()
    
    def create_image_version(self, post_id: int, image_type: str, 
                           image_data: bytes, metadata: Dict[str, Any]) -> str:
        """新しい画像バージョンを作成"""
        
        # 画像ハッシュ生成
        image_hash = hashlib.sha256(image_data).hexdigest()[:16]
        
        # バージョンID生成
        version_id = f"{post_id}_{image_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{image_hash}"
        
        # バージョン情報記録
        version_info = {
            "version_id": version_id,
            "post_id": post_id,
            "image_type": image_type,
            "created_at": datetime.now().isoformat(),
            "file_size": len(image_data),
            "image_hash": image_hash,
            "metadata": metadata
        }
        
        # データベース更新
        if post_id not in self.version_db:
            self.version_db[post_id] = {}
        
        if image_type not in self.version_db[post_id]:
            self.version_db[post_id][image_type] = []
        
        self.version_db[post_id][image_type].append(version_info)
        
        # バージョン履歴の制限（最新10件まで）
        if len(self.version_db[post_id][image_type]) > 10:
            self.version_db[post_id][image_type] = self.version_db[post_id][image_type][-10:]
        
        self._save_version_database()
        
        print(f"📸 画像バージョン作成: {version_id}")
        return version_id
    
    def get_image_history(self, post_id: int, image_type: str) -> List[Dict[str, Any]]:
        """画像の更新履歴取得"""
        return self.version_db.get(post_id, {}).get(image_type, [])
    
    def restore_image_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """指定バージョンの画像情報取得"""
        for post_id, image_types in self.version_db.items():
            for image_type, versions in image_types.items():
                for version in versions:
                    if version["version_id"] == version_id:
                        return version
        return None
    
    def _load_version_database(self):
        """バージョンデータベース読み込み"""
        db_file = self.base_dir / "image_version_db.json"
        if db_file.exists():
            try:
                with open(db_file, 'r', encoding='utf-8') as f:
                    self.version_db = json.load(f)
            except Exception as e:
                print(f"⚠️  バージョンDB読み込み失敗: {e}")
                self.version_db = {}
    
    def _save_version_database(self):
        """バージョンデータベース保存"""
        db_file = self.base_dir / "image_version_db.json"
        db_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(self.version_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  バージョンDB保存失敗: {e}")


class ImageAnalyzer:
    """画像分析・最適化システム"""
    
    def analyze_image_compatibility(self, old_image_data: bytes, 
                                  new_image_data: bytes) -> Dict[str, Any]:
        """画像の互換性分析"""
        
        try:
            # 画像サイズ・フォーマット分析
            old_img = Image.open(BytesIO(old_image_data))
            new_img = Image.open(BytesIO(new_image_data))
            
            analysis = {
                "size_compatibility": old_img.size == new_img.size,
                "format_compatibility": old_img.format == new_img.format,
                "aspect_ratio_old": old_img.width / old_img.height,
                "aspect_ratio_new": new_img.width / new_img.height,
                "size_difference_ratio": len(new_image_data) / len(old_image_data),
                "optimization_needed": len(new_image_data) > len(old_image_data) * 1.2
            }
            
            # 互換性スコア計算
            compatibility_score = 1.0
            if not analysis["size_compatibility"]:
                compatibility_score -= 0.3
            if not analysis["format_compatibility"]:
                compatibility_score -= 0.2
            if abs(analysis["aspect_ratio_old"] - analysis["aspect_ratio_new"]) > 0.1:
                compatibility_score -= 0.2
            if analysis["size_difference_ratio"] > 2.0:
                compatibility_score -= 0.3
            
            analysis["compatibility_score"] = max(0, compatibility_score)
            
            return analysis
            
        except Exception as e:
            return {"error": str(e), "compatibility_score": 0.0}
    
    def extract_style_profile(self, image_data: bytes) -> Dict[str, Any]:
        """画像スタイルプロファイル抽出"""
        
        try:
            img = Image.open(BytesIO(image_data))
            
            # 基本属性
            profile = {
                "dimensions": img.size,
                "format": img.format,
                "mode": img.mode,
                "file_size": len(image_data)
            }
            
            # 色彩分析（RGB画像の場合）
            if img.mode == "RGB":
                # 平均色計算
                pixels = list(img.getdata())
                avg_r = sum(p[0] for p in pixels) / len(pixels)
                avg_g = sum(p[1] for p in pixels) / len(pixels)
                avg_b = sum(p[2] for p in pixels) / len(pixels)
                
                profile["average_color"] = {
                    "r": int(avg_r),
                    "g": int(avg_g), 
                    "b": int(avg_b)
                }
                
                # 明度計算
                brightness = (avg_r * 0.299 + avg_g * 0.587 + avg_b * 0.114)
                profile["brightness"] = brightness
                profile["is_dark"] = brightness < 128
            
            return profile
            
        except Exception as e:
            return {"error": str(e)}


class ConsolidatedImageManager:
    """統合画像管理システム"""
    
    def __init__(self):
        """初期化"""
        # 画像設定を読み込み
        self.load_image_settings()
        
        # API設定
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.wordpress_api_key = os.getenv('WORDPRESS_API_KEY')
        self.wordpress_endpoint = os.getenv('WORDPRESS_ENDPOINT')
        
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        if not self.wordpress_api_key:
            raise ValueError("WORDPRESS_API_KEY not found in .env file")
        if not self.wordpress_endpoint:
            raise ValueError("WORDPRESS_ENDPOINT not found in .env file")
        
        # クライアント初期化
        self.google_client = genai.Client(api_key=self.google_api_key)
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
        self.imagen_model = 'imagen-3.0-generate-002'
        self.openai_image_model = 'gpt-image-1'
        
        # 管理システム初期化
        self.output_manager = OutputManager()
        self.version_manager = ImageVersionManager()
        self.analyzer = ImageAnalyzer()
        
        # 後方互換性のため
        self.outputs_dir = Path('outputs')
        self.outputs_dir.mkdir(exist_ok=True)
    
    def load_image_settings(self):
        """画像設定ファイルを読み込み"""
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'image_settings.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                self.image_settings = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load image settings: {e}")
            # デフォルト設定
            self.image_settings = {
                "eyecatch": {
                    "optimization": {
                        "enabled": True,
                        "target_max_size_kb": 500,
                        "target_dimensions": {"width": 1200, "height": 675},
                        "jpeg_quality": 85
                    }
                },
                "thumbnail": {
                    "optimization": {
                        "enabled": True,
                        "target_max_size_kb": 800,
                        "target_dimensions": {"width": 800, "height": 450},
                        "jpeg_quality": 80
                    }
                }
            }
    
    def optimize_image(self, image_data: bytes, image_type: str = 'eyecatch') -> bytes:
        """画像を最適化してファイルサイズを削減"""
        try:
            settings = self.image_settings.get(image_type, {}).get('optimization', {})
            
            if not settings.get('enabled', True):
                return image_data
            
            # PIL Imageで読み込み
            image = Image.open(BytesIO(image_data))
            
            # RGBA -> RGBに変換（JPEG保存のため）
            if image.mode in ('RGBA', 'LA'):
                # 白背景で合成
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[3])  # アルファチャンネルをマスクとして使用
                else:
                    background.paste(image)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 目標サイズにリサイズ
            target_dims = settings.get('target_dimensions', {})
            if target_dims.get('width') and target_dims.get('height'):
                target_size = (target_dims['width'], target_dims['height'])
                image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # JPEG品質を段階的に調整してファイルサイズを最適化
            target_size_kb = settings.get('target_max_size_kb', 500)
            base_quality = settings.get('jpeg_quality', 85)
            
            for quality in range(base_quality, 50, -5):  # 85から50まで5刻みで下げる
                output = BytesIO()
                save_kwargs = {
                    'format': 'JPEG',
                    'quality': quality,
                    'optimize': True,
                    'progressive': True
                }
                image.save(output, **save_kwargs)
                
                output_size_kb = output.tell() / 1024
                print(f"   Quality {quality}: {output_size_kb:.1f}KB")
                
                if output_size_kb <= target_size_kb:
                    print(f"✅ Optimized to {output_size_kb:.1f}KB (quality: {quality})")
                    return output.getvalue()
            
            # 最低品質でも目標サイズを超える場合は最低品質で保存
            output = BytesIO()
            image.save(output, format='JPEG', quality=50, optimize=True)
            final_size_kb = output.tell() / 1024
            print(f"⚠️  Final size: {final_size_kb:.1f}KB (minimum quality)")
            return output.getvalue()
            
        except Exception as e:
            print(f"❌ Image optimization failed: {e}")
            return image_data  # 最適化に失敗した場合は元の画像を返す
    
    def load_outline(self, outline_path: str) -> Dict:
        """アウトラインファイルを読み込み"""
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ファイル名からIDとタイムスタンプを抽出
            filename = Path(outline_path).stem
            match = re.search(r'(\d{8}_\d{6})_outline_(.+)', filename)
            if match:
                timestamp = match.group(1)
                outline_id = match.group(2)
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                outline_id = 'unknown'
            
            # タイトルを抽出
            title_match = re.search(r'Title:\s*(.+)', content)
            title = title_match.group(1) if title_match else 'Unknown Title'
            
            # 日付を生成
            date = datetime.now().strftime('%Y-%m-%d')
            
            return {
                'content': content,
                'timestamp': timestamp,
                'outline_id': outline_id,
                'filename': filename,
                'title': title,
                'date': date
            }
        except Exception as e:
            print(f"Error loading outline: {e}")
            return None
    
    def extract_chapters(self, outline_content: str) -> List[str]:
        """アウトラインから章タイトルを抽出"""
        chapters = []
        lines = outline_content.split('\n')
        
        for line in lines:
            # Blog Outline (TOC)セクションから章タイトルを抽出
            if re.match(r'^\d+\.\s+', line.strip()):
                chapter_title = re.sub(r'^\d+\.\s+', '', line.strip())
                chapters.append(chapter_title)
        
        return chapters
    
    def generate_prompt_with_gemini(self, template_file: str, outline_data: Dict, target_chapter: Optional[str] = None) -> str:
        """Geminiを使ってプロンプトテンプレートから画像生成プロンプトを作成"""
        try:
            # テンプレートファイルの絶対パスを構築
            if not os.path.isabs(template_file):
                template_path = project_root / 'templates' / template_file
            else:
                template_path = Path(template_file)
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 変数置換
            content = template.replace('{{outline}}', outline_data['content'])
            if target_chapter:
                content = content.replace('{{target_h2}}', target_chapter)
                # 章番号を抽出
                chapter_match = re.search(r'^(\d+)\.', target_chapter)
                chapter_number = chapter_match.group(1) if chapter_match else '1'
                content = content.replace('{{chapter_number}}', chapter_number)
            
            # Gemini Text APIでプロンプト生成を実行
            try:
                response = self.google_client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=content
                )
                return response.text
            except Exception as e:
                print(f"Warning: Gemini text generation failed: {e}")
                # フォールバック: テンプレートをそのまま使用
                return content
            
        except Exception as e:
            print(f"Error generating prompt: {e}")
            return None
    
    def extract_yaml_and_convert_to_prompt(self, generated_text: str) -> str:
        """生成されたテキストからYAML設定を抽出してImagen 3用プロンプトに変換"""
        try:
            # YAML部分を抽出
            yaml_start = generated_text.find('```yaml')
            yaml_end = generated_text.find('```', yaml_start + 7)
            
            if yaml_start != -1 and yaml_end != -1:
                yaml_content = generated_text[yaml_start + 7:yaml_end].strip()
                return self.yaml_to_imagen_prompt(yaml_content)
            else:
                # YAMLが見つからない場合は従来のプロンプト抽出を試行
                return self.extract_legacy_prompt(generated_text)
                
        except Exception as e:
            print(f"YAML processing failed, using fallback: {e}")
            return self.extract_legacy_prompt(generated_text)
    
    def yaml_to_imagen_prompt(self, yaml_content: str) -> str:
        """YAML設定をプロンプトに変換（OpenAI/Imagen対応）"""
        # YAML内の設定値を抽出
        style_match = re.search(r'style:\s*"([^"]+)"', yaml_content)
        theme_color_match = re.search(r'theme_color:\s*"([^"]+)"', yaml_content)
        mood_match = re.search(r'mood:\s*"([^"]+)"', yaml_content)
        background_type_match = re.search(r'type:\s*"([^"]+)"', yaml_content)
        background_color_match = re.search(r'color:\s*"([^"]+)"', yaml_content)
        
        # アイキャッチかサムネイルかを判定
        is_eyecatch = "text_support: true" in yaml_content or "main_title" in yaml_content
        
        if is_eyecatch:
            # アイキャッチ用（OpenAI gpt-image-1で日本語テキスト対応）
            main_text_matches = re.findall(r'content:\s*"([^"]+)"', yaml_content)
            
            # プロンプト構築（サムネイル風のクリエイティブスタイル + 日本語テキスト）
            prompt_parts = []
            
            # クリエイティブスタイル（サムネイル風）
            prompt_parts.append("Creative digital illustration")
            prompt_parts.append("featuring professional business person or educator")
            prompt_parts.append("in modern tech environment or classroom setting")
            prompt_parts.append("with futuristic elements and digital effects")
            
            # 日本語テキスト
            if main_text_matches:
                main_text = main_text_matches[0]
                prompt_parts.append(f"prominent Japanese text '{main_text}' displayed clearly")
                prompt_parts.append("professional typography with bold modern font")
            
            # スタイルと色彩（クリエイティブ）
            if style_match:
                style = style_match.group(1)
                prompt_parts.append(f"artistic style: {style}")
            
            if theme_color_match:
                colors = theme_color_match.group(1)
                prompt_parts.append(f"color scheme: {colors}")
            else:
                prompt_parts.append("vibrant blue and orange color palette")
            
            # 環境設定
            if background_type_match:
                bg_type = background_type_match.group(1)
                prompt_parts.append(f"background: {bg_type}")
            else:
                prompt_parts.append("modern office or educational environment")
            
            # 雰囲気
            if mood_match:
                mood = mood_match.group(1)
                prompt_parts.append(f"mood: {mood}")
            else:
                prompt_parts.append("professional and engaging atmosphere")
            
            # 品質設定
            prompt_parts.extend([
                "high quality digital art",
                "engaging visual composition",
                "modern and attractive design",
                "professional presentation style"
            ])
        
        else:
            # サムネイル用（Imagen 3でテキストなし）
            character_matches = re.findall(r'character_illustration[^}]*content:\s*"([^"]+)"', yaml_content)
            environment_matches = re.findall(r'contextual_background[^}]*content:\s*"([^"]+)"', yaml_content)
            dynamic_matches = re.findall(r'dynamic_objects[^}]*content:\s*"([^"]+)"', yaml_content)
            
            # プロンプト構築
            prompt_parts = []
            
            # スタイル
            if style_match:
                style = style_match.group(1)
                prompt_parts.append(f"Creative illustration, {style.lower()}")
            else:
                prompt_parts.append("Creative digital illustration")
            
            # キャラクター要素
            if character_matches:
                character_desc = character_matches[0]
                prompt_parts.append(f"featuring {character_desc}")
            
            # 環境・背景
            if environment_matches:
                env_desc = environment_matches[0]
                prompt_parts.append(f"in {env_desc}")
            elif background_type_match:
                bg_type = background_type_match.group(1)
                prompt_parts.append(f"environment: {bg_type}")
            
            # ダイナミック要素
            if dynamic_matches:
                dynamic_desc = dynamic_matches[0]
                prompt_parts.append(f"with {dynamic_desc}")
            
            # 色彩
            if theme_color_match:
                colors = theme_color_match.group(1)
                prompt_parts.append(f"color palette: {colors}")
            
            # 雰囲気
            if mood_match:
                mood = mood_match.group(1)
                prompt_parts.append(f"atmosphere: {mood}")
            
            # 基本設定（テキスト明確除外）
            prompt_parts.extend([
                "no text, no letters, no words",
                "pure visual storytelling",
                "16:9 aspect ratio",
                "high quality digital art",
                "detailed and immersive"
            ])
        
        final_prompt = ", ".join(prompt_parts)
        
        # 長さ制限
        if len(final_prompt) > 400:
            important_parts = final_prompt.split(", ")[:8]  # 重要な部分を保持
            final_prompt = ", ".join(important_parts)
        
        return final_prompt
    
    def extract_legacy_prompt(self, generated_text: str) -> str:
        """従来のプロンプト抽出方法（フォールバック）"""
        # DALL-E 3 Prompt: セクションを探す
        lines = generated_text.split('\n')
        prompt_lines = []
        in_prompt_section = False
        
        for line in lines:
            if 'DALL-E 3 Prompt:' in line or 'Prompt:' in line:
                in_prompt_section = True
                continue
            elif line.startswith('```') and in_prompt_section:
                if prompt_lines:  # 既にプロンプトを収集済みなら終了
                    break
                continue
            elif in_prompt_section and line.strip():
                if not line.startswith('**') and not line.startswith('#') and not line.startswith('-'):
                    prompt_lines.append(line.strip())
        
        extracted_prompt = ' '.join(prompt_lines) if prompt_lines else generated_text
        
        # プロンプトを最適化（短く簡潔に）
        if len(extracted_prompt) > 300:
            # より厳格に短縮
            important_parts = []
            for line in extracted_prompt.split('.'):
                line = line.strip()
                if line and any(keyword in line.lower() for keyword in ['style', 'professional', 'modern', 'clean', 'colors', 'blue']):
                    important_parts.append(line)
            
            if important_parts:
                extracted_prompt = '. '.join(important_parts[:3]) + '.'
            else:
                # フォールバック: 最初の200文字のみ
                extracted_prompt = extracted_prompt[:200].split('.')[0] + '.'
        
        return extracted_prompt
    
    def generate_image_openai(self, prompt: str) -> Optional[bytes]:
        """OpenAI gpt-image-1でアイキャッチ画像生成（日本語テキスト対応）"""
        try:
            print(f"🎨 Generating eyecatch with OpenAI: {prompt[:100]}...")
            
            response = self.openai_client.images.generate(
                model=self.openai_image_model,
                prompt=prompt,
                size="1536x1024",  # gpt-image-1の横長サイズ
                quality="high",
                n=1
            )
            
            # base64データを取得（gpt-image-1はbase64を返す）
            if response.data and len(response.data) > 0:
                image_base64 = response.data[0].b64_json
                return base64.b64decode(image_base64)
            else:
                print("No images generated by OpenAI")
                return None
                
        except Exception as e:
            print(f"Error generating image with OpenAI: {e}")
            return None
    
    def generate_image_imagen(self, prompt: str) -> Optional[bytes]:
        """Imagen 3でサムネイル画像生成（テキストなし）"""
        try:
            print(f"🎨 Generating thumbnail with Imagen 3: {prompt[:100]}...")
            
            response = self.google_client.models.generate_images(
                model=self.imagen_model,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="16:9",  # ブログ用の比率
                    safety_filter_level="block_low_and_above",
                    person_generation="allow_adult"
                )
            )
            
            # 最初の画像を取得
            if response.generated_images:
                generated_image = response.generated_images[0]
                return generated_image.image.image_bytes
            else:
                print("No images generated by Imagen 3")
                return None
                
        except Exception as e:
            print(f"Error generating image with Imagen 3: {e}")
            return None
    
    def extend_image_to_16_9(self, image: Image.Image) -> Image.Image:
        """1536×1024の画像を16:9（1920×1080）に拡張（ブラー延長）"""
        try:
            # 現在のサイズと目標サイズ
            current_width, current_height = image.size
            target_width, target_height = 1920, 1080
            
            print(f"📐 Extending image from {current_width}×{current_height} to {target_width}×{target_height}")
            
            # 新しいキャンバス作成
            extended_image = Image.new('RGB', (target_width, target_height), (0, 0, 0))
            
            # 元画像を中央に配置
            x_offset = (target_width - current_width) // 2
            y_offset = (target_height - current_height) // 2
            extended_image.paste(image, (x_offset, y_offset))
            
            # 左右の拡張（ブラー）
            if x_offset > 0:
                # 左端を拡張
                left_edge = image.crop((0, 0, 20, current_height))  # 左端20px
                left_blurred = left_edge.filter(ImageFilter.GaussianBlur(radius=3))
                left_stretched = left_blurred.resize((x_offset, current_height))
                extended_image.paste(left_stretched, (0, y_offset))
                
                # 右端を拡張
                right_edge = image.crop((current_width-20, 0, current_width, current_height))  # 右端20px
                right_blurred = right_edge.filter(ImageFilter.GaussianBlur(radius=3))
                right_stretched = right_blurred.resize((x_offset, current_height))
                extended_image.paste(right_stretched, (x_offset + current_width, y_offset))
            
            # 上下の拡張（ブラー）
            if y_offset > 0:
                # 上端を拡張（全幅で）
                top_edge = extended_image.crop((0, y_offset, target_width, y_offset + 20))  # 上端20px
                top_blurred = top_edge.filter(ImageFilter.GaussianBlur(radius=5))
                top_stretched = top_blurred.resize((target_width, y_offset))
                extended_image.paste(top_stretched, (0, 0))
                
                # 下端を拡張（全幅で）
                bottom_edge = extended_image.crop((0, y_offset + current_height - 20, target_width, y_offset + current_height))  # 下端20px
                bottom_blurred = bottom_edge.filter(ImageFilter.GaussianBlur(radius=5))
                bottom_stretched = bottom_blurred.resize((target_width, y_offset))
                extended_image.paste(bottom_stretched, (0, y_offset + current_height))
            
            # 角の部分をさらにブラーで自然に
            extended_image = extended_image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            print("✅ Image extended to 16:9 with blur padding")
            return extended_image
            
        except Exception as e:
            print(f"Warning: Image extension failed: {e}")
            return image  # 失敗時は元画像を返す
    
    def save_image(self, image_data: bytes, filename: str, metadata: Optional[Dict] = None, file_type: str = 'image', chapter: Optional[int] = None) -> str:
        """画像を自動分類して保存"""
        try:
            # 画像形式を判定
            try:
                image = Image.open(BytesIO(image_data))
                is_optimized_jpeg = image.format == 'JPEG'
            except:
                is_optimized_jpeg = False
            
            if is_optimized_jpeg:
                # 最適化済みJPEG画像の場合はそのまま保存
                if metadata:
                    filepath = self.output_manager.save_binary(image_data, metadata, file_type, chapter, extension='.jpg')
                else:
                    filepath = self.outputs_dir / filename.replace('.png', '.jpg')
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
            else:
                # PNG画像の場合は従来の処理
                image = Image.open(BytesIO(image_data))
                original_size = image.size
                
                # アイキャッチ画像（1536×1024）の場合は16:9に拡張
                if original_size == (1536, 1024):
                    print(f"🎨 Detected OpenAI eyecatch image, extending to 16:9...")
                    image = self.extend_image_to_16_9(image)
                
                # Web最適化
                if image.size[0] > 1920:  # 幅が1920pxより大きい場合リサイズ
                    ratio = 1920 / image.size[0]
                    new_size = (1920, int(image.size[1] * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # 保存処理
                if metadata:
                    # 新しい自動分類システムを使用
                    img_bytes = BytesIO()
                    image.save(img_bytes, 'PNG', optimize=True)
                    img_bytes.seek(0)
                    
                    filepath = self.output_manager.save_binary(img_bytes.getvalue(), metadata, file_type, chapter)
                else:
                    # 従来の方法（後方互換性）
                    filepath = self.outputs_dir / filename
                    image.save(filepath, 'PNG', optimize=True)
                filepath = str(filepath)
            
            print(f"✅ Image saved: {filepath} ({image.size[0]}x{image.size[1]})")
            return filepath
            
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    # ==== 新規画像生成機能 ====
    
    def generate_eyecatch(self, outline_data: Dict) -> Optional[str]:
        """アイキャッチ画像生成（OpenAI gpt-image-1使用）"""
        print("🖼️  Generating eyecatch image...")
        
        # プロンプト生成
        prompt_text = self.generate_prompt_with_gemini('eyecatch.md', outline_data)
        if not prompt_text:
            return None
        
        # YAML設定を抽出してプロンプトに変換
        image_prompt = self.extract_yaml_and_convert_to_prompt(prompt_text)
        
        # OpenAI gpt-image-1でアイキャッチ画像生成（日本語テキスト対応）
        image_data = self.generate_image_openai(image_prompt)
        if not image_data:
            return None
        
        # 画像を最適化（ファイルサイズ削減）
        print(f"📦 Optimizing eyecatch image...")
        original_size_kb = len(image_data) / 1024
        print(f"   Original size: {original_size_kb:.1f}KB")
        
        optimized_data = self.optimize_image(image_data, 'eyecatch')
        optimized_size_kb = len(optimized_data) / 1024
        print(f"   Final size: {optimized_size_kb:.1f}KB ({(1-optimized_size_kb/original_size_kb)*100:.1f}% reduction)")
        
        image_data = optimized_data
        
        # 自動分類して保存
        metadata = {
            'title': outline_data.get('title', ''),
            'date': outline_data.get('date', ''),
            'int_number': outline_data.get('outline_id', 'INT-01'),
            'timestamp': outline_data.get('timestamp', '')
        }
        return self.save_image(image_data, '', metadata, 'eyecatch')
    
    def generate_thumbnail(self, outline_data: Dict, chapter: str, chapter_num: int) -> Optional[str]:
        """サムネイル画像生成（Imagen 3使用、テキストなし）"""
        print(f"🖼️  Generating thumbnail for chapter {chapter_num}: {chapter[:50]}...")
        
        # プロンプト生成
        prompt_text = self.generate_prompt_with_gemini('thumbnail.md', outline_data, chapter)
        if not prompt_text:
            return None
        
        # YAML設定を抽出してプロンプトに変換
        image_prompt = self.extract_yaml_and_convert_to_prompt(prompt_text)
        
        # Imagen 3でサムネイル画像生成（テキストなし）
        image_data = self.generate_image_imagen(image_prompt)
        if not image_data:
            return None
        
        # 画像を最適化（ファイルサイズ削減）
        print(f"📦 Optimizing thumbnail image...")
        original_size_kb = len(image_data) / 1024
        print(f"   Original size: {original_size_kb:.1f}KB")
        
        optimized_data = self.optimize_image(image_data, 'thumbnail')
        optimized_size_kb = len(optimized_data) / 1024
        print(f"   Final size: {optimized_size_kb:.1f}KB ({(1-optimized_size_kb/original_size_kb)*100:.1f}% reduction)")
        
        image_data = optimized_data
        
        # 自動分類して保存
        metadata = {
            'title': outline_data.get('title', ''),
            'date': outline_data.get('date', ''),
            'int_number': outline_data.get('outline_id', 'INT-01'),
            'timestamp': outline_data.get('timestamp', '')
        }
        return self.save_image(image_data, '', metadata, 'thumbnail', chapter_num)
    
    def generate_all_images(self, outline_path: str) -> Dict:
        """全画像生成"""
        results = {
            'eyecatch': None,
            'thumbnails': [],
            'errors': []
        }
        
        # アウトライン読み込み
        outline_data = self.load_outline(outline_path)
        if not outline_data:
            results['errors'].append("Failed to load outline")
            return results
        
        # 章抽出
        chapters = self.extract_chapters(outline_data['content'])
        print(f"📚 Found {len(chapters)} chapters")
        
        # アイキャッチ生成
        print("\n" + "="*50)
        print("EYECATCH GENERATION")
        print("="*50)
        try:
            eyecatch_path = self.generate_eyecatch(outline_data)
            results['eyecatch'] = eyecatch_path
            if eyecatch_path:
                print(f"✅ Eyecatch completed: {eyecatch_path}")
            else:
                print("❌ Eyecatch generation failed")
        except Exception as e:
            error_msg = f"Eyecatch generation failed: {e}"
            results['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        # サムネイル生成
        print("\n" + "="*50)
        print("THUMBNAIL GENERATION")
        print("="*50)
        for i, chapter in enumerate(chapters, 1):
            try:
                thumbnail_path = self.generate_thumbnail(outline_data, chapter, i)
                if thumbnail_path:
                    results['thumbnails'].append(thumbnail_path)
                    print(f"✅ Chapter {i} completed: {thumbnail_path}")
                else:
                    print(f"❌ Chapter {i} generation failed")
            except Exception as e:
                error_msg = f"Thumbnail {i} generation failed: {e}"
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
        
        return results
    
    # ==== WordPress画像更新機能 ====
    
    def get_wordpress_post(self, post_id: int) -> Optional[Dict]:
        """WordPress記事情報を取得"""
        try:
            headers = {
                'X-API-Key': self.wordpress_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{self.wordpress_endpoint}/get-post/{post_id}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get post {post_id}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting post {post_id}: {e}")
            return None
    
    def upload_image_to_wordpress(self, image_data: bytes, filename: str) -> Optional[int]:
        """WordPress メディアライブラリに画像をアップロード"""
        try:
            headers = {'X-API-Key': self.wordpress_api_key}
            
            files = {
                'file': (filename, BytesIO(image_data), 'image/jpeg')
            }
            
            response = requests.post(
                f'{self.wordpress_endpoint}/upload-image',
                headers=headers,
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                attachment_id = result.get('attachment_id')
                print(f"📤 Upload successful: ID {attachment_id}")
                return attachment_id
            else:
                print(f"❌ Upload failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return None
    
    def update_wordpress_featured_image(self, post_id: int, attachment_id: int) -> bool:
        """WordPressの記事のアイキャッチ画像を更新"""
        try:
            headers = {
                'X-API-Key': self.wordpress_api_key,
                'Content-Type': 'application/json'
            }
            
            update_data = {'featured_image_id': attachment_id}
            
            response = requests.post(
                f'{self.wordpress_endpoint}/update-post/{post_id}',
                headers=headers,
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print("🔄 Featured image updated successfully!")
                return True
            else:
                print(f"❌ Featured image update failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Featured image update error: {e}")
            return False
    
    def update_eyecatch_wordpress(self, post_id: int, custom_prompt: Optional[str] = None) -> bool:
        """WordPressのアイキャッチ画像を更新"""
        print(f"🚀 Updating eyecatch for post {post_id}")
        
        # 1. 記事情報取得
        post_data = self.get_wordpress_post(post_id)
        if not post_data:
            return False
        
        title = post_data.get('title', '')
        print(f"📖 Post title: {title}")
        
        # 2. 画像生成
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f'Modern professional digital illustration for blog article titled "{title}". Clean tech design with blue/purple gradient background. Japanese text "{title}" prominently displayed. High-quality contemporary style.'
        
        print("🎨 Generating image with gpt-image-1...")
        image_data = self.generate_image_openai(prompt)
        if not image_data:
            return False
        
        # 3. 画像最適化
        print("📦 Optimizing image...")
        original_size_kb = len(image_data) / 1024
        print(f"   Original size: {original_size_kb:.1f}KB")
        
        optimized_data = self.optimize_image(image_data, 'eyecatch')
        optimized_size_kb = len(optimized_data) / 1024
        print(f"   Final size: {optimized_size_kb:.1f}KB ({(1-optimized_size_kb/original_size_kb)*100:.1f}% reduction)")
        
        # 4. ローカル保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'eyecatch_{post_id}_{timestamp}.jpg'
        local_path = self.outputs_dir / filename
        
        with open(local_path, 'wb') as f:
            f.write(optimized_data)
        print(f"💾 Image saved locally: {local_path}")
        
        # 5. WordPress アップロード
        attachment_id = self.upload_image_to_wordpress(optimized_data, filename)
        if not attachment_id:
            return False
        
        # 6. アイキャッチ更新
        success = self.update_wordpress_featured_image(post_id, attachment_id)
        if not success:
            return False
        
        # 7. バージョン管理
        metadata = {
            'post_id': post_id,
            'title': title,
            'prompt': prompt,
            'attachment_id': attachment_id,
            'method': 'wp_update',
            'timestamp': timestamp
        }
        
        version_id = self.version_manager.create_image_version(
            post_id, 'eyecatch', optimized_data, metadata
        )
        
        # 8. 検証
        print("🔍 Verifying update...")
        base_url = self.wordpress_endpoint.replace('/wp-json/blog-generator/v1', '')
        verify_response = requests.get(f'{base_url}/wp-json/wp/v2/posts/{post_id}')
        
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            current_id = verify_data.get('featured_media', 0)
            
            if current_id == attachment_id:
                print(f"🎉 Update completed! Eyecatch ID: {current_id}, Version: {version_id}")
                return True
            else:
                print(f"⚠️ Verification mismatch: expected {attachment_id}, got {current_id}")
                return False
        else:
            print("❌ Verification API failed")
            return False
    
    def update_chapter_image_wordpress(self, post_id: int, chapter_num: int, custom_prompt: Optional[str] = None) -> bool:
        """WordPressの章画像を更新"""
        print(f"🚀 Updating chapter {chapter_num} image for post {post_id}")
        
        # 1. 記事情報取得
        post_data = self.get_wordpress_post(post_id)
        if not post_data:
            return False
        
        title = post_data.get('title', '')
        print(f"📖 Post title: {title}")
        
        # 2. 画像生成
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f'Chapter {chapter_num} illustration for "{title}". Professional modern design, clean visual style, no text, 16:9 aspect ratio, high quality digital art.'
        
        print(f"🎨 Generating chapter {chapter_num} image with Imagen 3...")
        image_data = self.generate_image_imagen(prompt)
        if not image_data:
            return False
        
        # 3. 画像最適化
        print("📦 Optimizing image...")
        original_size_kb = len(image_data) / 1024
        print(f"   Original size: {original_size_kb:.1f}KB")
        
        optimized_data = self.optimize_image(image_data, 'thumbnail')
        optimized_size_kb = len(optimized_data) / 1024
        print(f"   Final size: {optimized_size_kb:.1f}KB ({(1-optimized_size_kb/original_size_kb)*100:.1f}% reduction)")
        
        # 4. ローカル保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'chapter_{chapter_num}_{post_id}_{timestamp}.jpg'
        local_path = self.outputs_dir / filename
        
        with open(local_path, 'wb') as f:
            f.write(optimized_data)
        print(f"💾 Image saved locally: {local_path}")
        
        # 5. WordPress アップロード
        attachment_id = self.upload_image_to_wordpress(optimized_data, filename)
        if not attachment_id:
            return False
        
        # 6. バージョン管理
        metadata = {
            'post_id': post_id,
            'title': title,
            'chapter_num': chapter_num,
            'prompt': prompt,
            'attachment_id': attachment_id,
            'method': 'wp_update',
            'timestamp': timestamp
        }
        
        version_id = self.version_manager.create_image_version(
            post_id, f'chapter_{chapter_num}', optimized_data, metadata
        )
        
        print(f"🎉 Chapter {chapter_num} image updated! Attachment ID: {attachment_id}, Version: {version_id}")
        return True
    
    # ==== バージョン管理機能 ====
    
    def show_image_history(self, post_id: int, image_type: str = None) -> None:
        """画像の更新履歴を表示"""
        print(f"📋 Image history for post {post_id}")
        
        if image_type:
            history = self.version_manager.get_image_history(post_id, image_type)
            if history:
                print(f"\n{image_type} history:")
                for i, version in enumerate(history, 1):
                    created_at = version.get('created_at', 'Unknown')
                    file_size = version.get('file_size', 0) / 1024
                    version_id = version.get('version_id', 'Unknown')
                    print(f"  {i}. {created_at} - {file_size:.1f}KB - {version_id}")
            else:
                print(f"No history found for {image_type}")
        else:
            # 全タイプの履歴を表示
            if post_id in self.version_manager.version_db:
                for img_type, history in self.version_manager.version_db[post_id].items():
                    print(f"\n{img_type} history:")
                    for i, version in enumerate(history, 1):
                        created_at = version.get('created_at', 'Unknown')
                        file_size = version.get('file_size', 0) / 1024
                        version_id = version.get('version_id', 'Unknown')
                        print(f"  {i}. {created_at} - {file_size:.1f}KB - {version_id}")
            else:
                print("No history found for this post")
    
    def restore_image_version(self, version_id: str) -> bool:
        """指定バージョンの画像を復元"""
        print(f"🔄 Restoring image version: {version_id}")
        
        version_info = self.version_manager.restore_image_version(version_id)
        if not version_info:
            print("❌ Version not found")
            return False
        
        print(f"Found version: {version_info['created_at']}")
        print(f"Post ID: {version_info['post_id']}")
        print(f"Image type: {version_info['image_type']}")
        print(f"File size: {version_info['file_size'] / 1024:.1f}KB")
        
        # 実際の復元処理はメタデータのみ表示
        # 実装時はWordPressへの再アップロードと更新処理を追加
        print("⚠️  Restoration feature requires WordPress re-upload implementation")
        return True


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(
        description='Consolidated Image Manager - 統合画像管理システム',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 新規画像生成
  python consolidated_image_manager.py generate --outline outputs/final_articles/article/outline.md --mode eyecatch
  python consolidated_image_manager.py generate --outline outputs/final_articles/article/outline.md --mode all
  
  # WordPress画像更新
  python consolidated_image_manager.py update --post-id 1234 --type eyecatch
  python consolidated_image_manager.py update --post-id 1234 --type chapter --chapter-num 1
  
  # 簡単更新（後方互換性）
  python consolidated_image_manager.py quick-update 1234
  
  # バージョン管理
  python consolidated_image_manager.py version --post-id 1234 --action history
  python consolidated_image_manager.py version --post-id 1234 --action restore --version-id VERSION_ID
        """
    )
    
    # サブコマンド
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # generate サブコマンド
    generate_parser = subparsers.add_parser('generate', help='Generate new images')
    generate_parser.add_argument('--outline', required=True, help='Path to outline file')
    generate_parser.add_argument('--mode', choices=['eyecatch', 'thumbnail', 'all'], 
                                default='all', help='Generation mode')
    generate_parser.add_argument('--chapter', type=int, help='Chapter number for thumbnail mode')
    
    # update サブコマンド
    update_parser = subparsers.add_parser('update', help='Update WordPress images')
    update_parser.add_argument('--post-id', type=int, required=True, help='WordPress post ID')
    update_parser.add_argument('--type', choices=['eyecatch', 'chapter'], 
                              required=True, help='Image type to update')
    update_parser.add_argument('--chapter-num', type=int, help='Chapter number (required for chapter type)')
    update_parser.add_argument('--prompt', help='Custom prompt for image generation')
    
    # quick-update サブコマンド（後方互換性）
    quick_parser = subparsers.add_parser('quick-update', help='Quick eyecatch update (legacy compatibility)')
    quick_parser.add_argument('post_id', type=int, help='WordPress post ID')
    quick_parser.add_argument('--prompt', help='Custom prompt for image generation')
    
    # version サブコマンド
    version_parser = subparsers.add_parser('version', help='Version management')
    version_parser.add_argument('--post-id', type=int, required=True, help='WordPress post ID')
    version_parser.add_argument('--action', choices=['history', 'restore'], 
                               required=True, help='Version action')
    version_parser.add_argument('--type', help='Image type for history')
    version_parser.add_argument('--version-id', help='Version ID for restore')
    
    args = parser.parse_args()
    
    # コマンドが指定されていない場合はヘルプを表示
    if not args.command:
        parser.print_help()
        return
    
    try:
        print("🚀 Consolidated Image Manager")
        print("="*50)
        
        manager = ConsolidatedImageManager()
        
        # generate コマンド
        if args.command == 'generate':
            if args.mode == 'all':
                results = manager.generate_all_images(args.outline)
                
                print("\n" + "="*50)
                print("GENERATION SUMMARY")
                print("="*50)
                print(f"📊 Eyecatch: {'✅ Success' if results['eyecatch'] else '❌ Failed'}")
                print(f"📊 Thumbnails: {len(results['thumbnails'])} generated")
                
                if results['eyecatch']:
                    print(f"   📄 {results['eyecatch']}")
                
                for thumb in results['thumbnails']:
                    print(f"   📄 {thumb}")
                    
                if results['errors']:
                    print(f"\n⚠️  Errors encountered:")
                    for error in results['errors']:
                        print(f"   ❌ {error}")
                        
            elif args.mode == 'eyecatch':
                outline_data = manager.load_outline(args.outline)
                if outline_data:
                    path = manager.generate_eyecatch(outline_data)
                    if path:
                        print(f"✅ Eyecatch generated: {path}")
                    else:
                        print("❌ Eyecatch generation failed")
                        
            elif args.mode == 'thumbnail':
                if not args.chapter:
                    print("❌ --chapter required for thumbnail mode")
                    return
                
                outline_data = manager.load_outline(args.outline)
                if outline_data:
                    chapters = manager.extract_chapters(outline_data['content'])
                    if args.chapter <= len(chapters):
                        chapter = chapters[args.chapter - 1]
                        path = manager.generate_thumbnail(outline_data, chapter, args.chapter)
                        if path:
                            print(f"✅ Thumbnail generated: {path}")
                        else:
                            print("❌ Thumbnail generation failed")
                    else:
                        print(f"❌ Chapter {args.chapter} not found (available: 1-{len(chapters)})")
        
        # update コマンド
        elif args.command == 'update':
            if args.type == 'eyecatch':
                success = manager.update_eyecatch_wordpress(args.post_id, args.prompt)
                if success:
                    print("✅ Eyecatch update completed!")
                else:
                    print("❌ Eyecatch update failed!")
                    
            elif args.type == 'chapter':
                if not args.chapter_num:
                    print("❌ --chapter-num required for chapter type")
                    return
                
                success = manager.update_chapter_image_wordpress(
                    args.post_id, args.chapter_num, args.prompt
                )
                if success:
                    print(f"✅ Chapter {args.chapter_num} image update completed!")
                else:
                    print(f"❌ Chapter {args.chapter_num} image update failed!")
        
        # quick-update コマンド（後方互換性）
        elif args.command == 'quick-update':
            success = manager.update_eyecatch_wordpress(args.post_id, args.prompt)
            sys.exit(0 if success else 1)
        
        # version コマンド
        elif args.command == 'version':
            if args.action == 'history':
                manager.show_image_history(args.post_id, args.type)
            elif args.action == 'restore':
                if not args.version_id:
                    print("❌ --version-id required for restore action")
                    return
                success = manager.restore_image_version(args.version_id)
                if success:
                    print("✅ Version restoration completed!")
                else:
                    print("❌ Version restoration failed!")
                    
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()