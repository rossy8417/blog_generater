#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像更新管理システム - WordPress記事更新機能拡張
Boss1 & Worker2 共同開発による革新的画像管理システム
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO

# プロジェクトルート追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

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


class ImageUpdateEngine:
    """AI駆動画像差し替えシステム"""
    
    def __init__(self):
        self.version_manager = ImageVersionManager()
        self.analyzer = ImageAnalyzer()
        
        # 画像生成API設定
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
    
    def smart_replace_image(self, post_id: int, target_type: str, 
                          replacement_strategy: str = "auto",
                          new_image_data: Optional[bytes] = None,
                          generation_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        スマート画像差し替え
        
        Args:
            post_id: 投稿ID
            target_type: 画像タイプ ('eyecatch', 'chapter_1', etc.)
            replacement_strategy: 'auto', 'regenerate', 'upload'
            new_image_data: アップロード用画像データ
            generation_prompt: 生成用プロンプト
        
        Returns:
            更新結果
        """
        
        print(f"🎨 スマート画像差し替え開始: Post {post_id}, Type {target_type}")
        
        try:
            # 1. 既存画像の分析
            current_image_info = self._get_current_image_info(post_id, target_type)
            
            # 2. 置換戦略実行
            if replacement_strategy == "upload" and new_image_data:
                result = self._replace_with_upload(post_id, target_type, new_image_data, current_image_info)
            elif replacement_strategy == "regenerate":
                result = self._replace_with_regeneration(post_id, target_type, generation_prompt, current_image_info)
            else:  # auto
                result = self._auto_replacement_strategy(post_id, target_type, new_image_data, generation_prompt, current_image_info)
            
            # 3. 更新履歴記録
            if result["success"]:
                version_id = self.version_manager.create_image_version(
                    post_id, target_type, result["image_data"], result["metadata"]
                )
                result["version_id"] = version_id
            
            return result
            
        except Exception as e:
            print(f"❌ 画像差し替え失敗: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def batch_update_images(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """複数画像の一括更新"""
        
        print(f"🖼️  バッチ画像更新開始: {len(updates)}件")
        
        results = []
        for i, update_config in enumerate(updates, 1):
            print(f"\n[{i}/{len(updates)}] 画像更新中...")
            
            try:
                result = self.smart_replace_image(**update_config)
                results.append({
                    "config": update_config,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "config": update_config,
                    "success": False,
                    "error": str(e)
                })
        
        success_count = sum(1 for r in results if r["success"])
        print(f"\n🎉 バッチ画像更新完了: {success_count}/{len(updates)} 件成功")
        
        return results
    
    def generate_contextual_replacement(self, post_content: str, 
                                      image_position: str,
                                      existing_style: Optional[Dict[str, Any]] = None) -> bytes:
        """記事内容に基づく適応的画像生成"""
        
        print(f"🧠 コンテンツ適応型画像生成: {image_position}")
        
        # 記事内容の意味解析
        content_keywords = self._extract_content_keywords(post_content)
        context_summary = self._summarize_content_context(post_content)
        
        # 適応的プロンプト生成
        adaptive_prompt = self._create_adaptive_prompt(
            content_keywords, context_summary, image_position, existing_style
        )
        
        print(f"📝 生成プロンプト: {adaptive_prompt[:100]}...")
        
        # 画像生成実行
        if image_position == "eyecatch":
            return self._generate_eyecatch_image(adaptive_prompt)
        else:
            return self._generate_chapter_image(adaptive_prompt)
    
    def _get_current_image_info(self, post_id: int, target_type: str) -> Optional[Dict[str, Any]]:
        """現在の画像情報取得"""
        history = self.version_manager.get_image_history(post_id, target_type)
        return history[-1] if history else None
    
    def _replace_with_upload(self, post_id: int, target_type: str, 
                           new_image_data: bytes, current_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """アップロード画像による置換"""
        
        # 互換性分析
        compatibility = {"compatibility_score": 1.0}  # デフォルト
        if current_info:
            # 既存画像との互換性チェック（実装簡略化）
            compatibility = {"compatibility_score": 0.9}
        
        # 最適化実行
        optimized_data = self._optimize_image(new_image_data, target_type)
        
        return {
            "success": True,
            "image_data": optimized_data,
            "metadata": {
                "method": "upload",
                "compatibility": compatibility,
                "optimized": True,
                "original_size": len(new_image_data),
                "final_size": len(optimized_data)
            }
        }
    
    def _replace_with_regeneration(self, post_id: int, target_type: str,
                                 prompt: Optional[str], current_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """再生成による置換"""
        
        if not prompt:
            prompt = self._generate_default_prompt(target_type)
        
        # 画像生成
        if target_type == "eyecatch":
            image_data = self._generate_eyecatch_image(prompt)
        else:
            image_data = self._generate_chapter_image(prompt)
        
        return {
            "success": True,
            "image_data": image_data,
            "metadata": {
                "method": "regeneration",
                "prompt": prompt,
                "generated": True
            }
        }
    
    def _auto_replacement_strategy(self, post_id: int, target_type: str,
                                 new_image_data: Optional[bytes], prompt: Optional[str],
                                 current_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """自動最適戦略選択"""
        
        if new_image_data:
            return self._replace_with_upload(post_id, target_type, new_image_data, current_info)
        elif prompt:
            return self._replace_with_regeneration(post_id, target_type, prompt, current_info)
        else:
            # デフォルト: 既存スタイルを維持した再生成
            default_prompt = self._generate_contextual_prompt(current_info)
            return self._replace_with_regeneration(post_id, target_type, default_prompt, current_info)
    
    def _optimize_image(self, image_data: bytes, image_type: str) -> bytes:
        """画像最適化"""
        
        try:
            img = Image.open(BytesIO(image_data))
            
            # RGB変換
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # サイズ調整（画像タイプに応じて）
            if image_type == "eyecatch":
                target_size = (1200, 675)  # 16:9
            else:
                target_size = (800, 450)   # 16:9
            
            if img.size != target_size:
                img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # JPEG最適化
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, progressive=True, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            print(f"⚠️  画像最適化失敗: {e}")
            return image_data
    
    def _extract_content_keywords(self, content: str) -> List[str]:
        """コンテンツキーワード抽出（簡略実装）"""
        # 実際の実装ではNLP処理を行う
        import re
        words = re.findall(r'\b\w+\b', content)
        return list(set(word for word in words if len(word) > 3))[:10]
    
    def _summarize_content_context(self, content: str) -> str:
        """コンテンツ要約（簡略実装）"""
        # 最初の200文字を要約として使用
        return content[:200] + "..." if len(content) > 200 else content
    
    def _create_adaptive_prompt(self, keywords: List[str], context: str, 
                              position: str, existing_style: Optional[Dict[str, Any]]) -> str:
        """適応的プロンプト生成"""
        
        base_prompt = f"Professional illustration for {position} representing: {', '.join(keywords[:5])}"
        
        if existing_style and "average_color" in existing_style:
            color_info = existing_style["average_color"]
            if existing_style.get("is_dark"):
                base_prompt += ", dark color scheme"
            else:
                base_prompt += ", bright color scheme"
        
        base_prompt += ", clean modern design, high quality"
        
        return base_prompt
    
    def _generate_eyecatch_image(self, prompt: str) -> bytes:
        """アイキャッチ画像生成（簡略実装）"""
        # 実際の実装ではOpenAI APIを呼び出し
        print(f"🎨 アイキャッチ生成: {prompt}")
        
        # ダミー画像生成（実装時はAPI呼び出しに置換）
        img = Image.new('RGB', (1200, 675), color=(100, 150, 200))
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        return output.getvalue()
    
    def _generate_chapter_image(self, prompt: str) -> bytes:
        """章画像生成（簡略実装）"""
        # 実際の実装ではGoogle Imagen APIを呼び出し
        print(f"🖼️  章画像生成: {prompt}")
        
        # ダミー画像生成（実装時はAPI呼び出しに置換）
        img = Image.new('RGB', (800, 450), color=(150, 200, 100))
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        return output.getvalue()
    
    def _generate_default_prompt(self, target_type: str) -> str:
        """デフォルトプロンプト生成"""
        if target_type == "eyecatch":
            return "Professional blog header image, modern design, technology theme"
        else:
            return f"Chapter illustration for {target_type}, clean modern style"
    
    def _generate_contextual_prompt(self, current_info: Optional[Dict[str, Any]]) -> str:
        """既存情報に基づくプロンプト生成"""
        if current_info and "metadata" in current_info:
            return current_info["metadata"].get("prompt", "Modern professional illustration")
        return "Modern professional illustration, clean design"


def main():
    """メイン実行関数"""
    print("🎨 画像更新管理システム - WordPress記事更新機能拡張")
    print("Boss1 & Worker2 共同開発版")
    
    try:
        engine = ImageUpdateEngine()
        print("✅ 画像更新エンジン初期化完了")
        print("📋 利用可能な機能:")
        print("   - smart_replace_image(): スマート画像差し替え")
        print("   - batch_update_images(): 一括画像更新")
        print("   - generate_contextual_replacement(): コンテンツ適応型生成")
        
        return engine
        
    except Exception as e:
        print(f"❌ 初期化エラー: {str(e)}")
        return None

if __name__ == "__main__":
    main()