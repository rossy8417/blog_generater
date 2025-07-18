#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Intent Extractor - 検索意図分析から複数のINT候補を抽出
config/intent_analysis_template.yamlの分析結果から、メイン意図以外のサブ意図を抽出し、
高意図レベルのものを新しいINT候補として記録する
"""

import json
import re
from datetime import datetime
from typing import Dict, List

def extract_sub_intents(analysis_result: str) -> List[Dict]:
    """
    検索意図分析結果から複数の意図を抽出
    
    Args:
        analysis_result: config/intent_analysis_template.yamlによる分析結果テキスト
        
    Returns:
        抽出されたサブ意図のリスト
    """
    sub_intents = []
    
    # Combined-Intent Summary セクションを抽出
    summary_section = re.search(
        r'Combined-Intent Summary.*?(?=##|Action Plan|$)', 
        analysis_result, 
        re.DOTALL | re.IGNORECASE
    )
    
    if not summary_section:
        return sub_intents
    
    summary_text = summary_section.group(0)
    
    # 箇条書き項目を抽出（メイン意図以外）
    intent_items = re.findall(r'[-*•]\s*(.+)', summary_text)
    
    for i, intent_text in enumerate(intent_items):
        # メイン意図をスキップ
        if i == 0 and any(word in intent_text.lower() for word in ['メイン', '主要', '基本']):
            continue
            
        # サブ意図として処理
        sub_intent = {
            "original_text": intent_text.strip(),
            "intent_type": classify_intent_type(intent_text),
            "intent_level": calculate_intent_level(intent_text),
            "suggested_keyword": generate_keyword_from_intent(intent_text),
            "target_audience": extract_target_audience(intent_text),
            "differentiation_factor": extract_differentiation_factor(intent_text)
        }
        
        sub_intents.append(sub_intent)
    
    return sub_intents

def classify_intent_type(intent_text: str) -> str:
    """意図タイプを分類"""
    text_lower = intent_text.lower()
    
    if any(word in text_lower for word in ['セキュリティ', 'リスク', 'プライバシー', '安全']):
        return 'セキュリティ・リスク管理'
    elif any(word in text_lower for word in ['コスト', '費用', '予算', '投資', 'roi']):
        return 'コスト・投資効果'
    elif any(word in text_lower for word in ['中小企業', 'sme', '小規模', '限られた']):
        return '中小企業特化'
    elif any(word in text_lower for word in ['従業員', '雇用', 'スキル', '人材', '教育']):
        return '人材・スキル影響'
    elif any(word in text_lower for word in ['競合', '他社', '事例', '導入状況', '市場']):
        return '市場・競合分析'
    elif any(word in text_lower for word in ['業界', '特化', '専門', '分野']):
        return '業界特化'
    else:
        return 'その他'

def calculate_intent_level(intent_text: str) -> str:
    """意図レベルを計算"""
    text_lower = intent_text.lower()
    score = 0
    
    # 高意図レベルの指標
    high_indicators = [
        '方法', '手順', 'ガイド', '導入', '実装', '選び方', '比較',
        '効果', '成果', 'roi', 'コスト', '予算', 'セキュリティ',
        '対策', '解決', '課題', '問題', '不安', '心配'
    ]
    
    for indicator in high_indicators:
        if indicator in text_lower:
            score += 1
    
    # 具体性の確認
    if any(word in text_lower for word in ['具体的', '実際', '実用', '実践']):
        score += 1
    
    # 緊急性の確認
    if any(word in text_lower for word in ['急ぎ', '早急', 'すぐ', '今すぐ']):
        score += 1
    
    if score >= 3:
        return '高'
    elif score >= 1:
        return '中'
    else:
        return '低'

def generate_keyword_from_intent(intent_text: str) -> str:
    """意図からキーワードを生成"""
    text_lower = intent_text.lower()
    
    # キーワードマッピング
    keyword_mapping = {
        'セキュリティ': 'AI セキュリティ 対策',
        'リスク': 'AI 導入 リスク',
        'コスト': 'AI 導入 コスト',
        '中小企業': 'AI 中小企業 導入',
        '従業員': 'AI 従業員 影響',
        'スキル': 'AI スキル 変化',
        '競合': 'AI 導入 事例',
        '業界': 'AI 業界別 活用'
    }
    
    for key, keyword in keyword_mapping.items():
        if key in text_lower:
            return keyword
    
    return 'AI 活用 方法'

def extract_target_audience(intent_text: str) -> str:
    """対象読者を抽出"""
    text_lower = intent_text.lower()
    
    if '中小企業' in text_lower:
        return '中小企業経営者・管理者'
    elif 'セキュリティ' in text_lower:
        return 'IT担当者・セキュリティ責任者'
    elif 'コスト' in text_lower:
        return '経営者・予算決定者'
    elif '従業員' in text_lower:
        return 'HR担当者・管理職'
    else:
        return '一般ビジネスパーソン'

def extract_differentiation_factor(intent_text: str) -> str:
    """差別化要因を抽出"""
    text_lower = intent_text.lower()
    
    if 'セキュリティ' in text_lower:
        return 'セキュリティ・リスク管理に特化'
    elif '中小企業' in text_lower:
        return '中小企業の制約・条件に特化'
    elif 'コスト' in text_lower:
        return '投資効果・コスト分析に特化'
    elif '従業員' in text_lower:
        return '人材・組織面の影響に特化'
    else:
        return '特定の観点・課題に特化'

def process_multi_intent_analysis(original_keyword: str, analysis_result: str) -> Dict:
    """
    複数意図分析を処理し、新しいINT候補を記録
    
    Args:
        original_keyword: 元のキーワード（例：「生成AI 定型業務 自動化」）
        analysis_result: config/intent_analysis_template.yamlによる分析結果
        
    Returns:
        処理結果
    """
    # intent_tracker.jsonを読み込み
    try:
        with open('intent_tracker.json', 'r', encoding='utf-8') as f:
            tracker = json.load(f)
    except:
        tracker = {
            'analyzed_intents': [],
            'pending_high_intent_keywords': [],
            'next_int_number': 2
        }
    
    # サブ意図を抽出
    sub_intents = extract_sub_intents(analysis_result)
    
    new_int_candidates = []
    recorded_intents = []
    
    for sub_intent in sub_intents:
        # 高意図レベルかつ既存と差別化されているかチェック
        if sub_intent['intent_level'] == '高':
            # 差別化スコア計算（簡易版）
            differentiation_score = calculate_differentiation_score(
                sub_intent, 
                tracker.get('analyzed_intents', [])
            )
            
            if differentiation_score >= 6:
                # 新しいINT候補として記録
                int_number = f"INT-{tracker['next_int_number']:02d}"
                
                new_candidate = {
                    "keyword": sub_intent['suggested_keyword'],
                    "original_analysis_keyword": original_keyword,
                    "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                    "intent_level": sub_intent['intent_level'],
                    "intent_type": sub_intent['intent_type'],
                    "target_audience": sub_intent['target_audience'],
                    "differentiation_factor": sub_intent['differentiation_factor'],
                    "differentiation_score": differentiation_score,
                    "assigned_int": int_number,
                    "status": "pending",
                    "source_intent": sub_intent['original_text'],
                    "recommended_priority": "高"
                }
                
                new_int_candidates.append(new_candidate)
                tracker['next_int_number'] += 1
                
            else:
                # 記録のみ
                recorded_intent = {
                    "keyword": sub_intent['suggested_keyword'],
                    "original_analysis_keyword": original_keyword,
                    "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                    "intent_level": sub_intent['intent_level'],
                    "differentiation_score": differentiation_score,
                    "status": "recorded_low_differentiation",
                    "notes": f"高意図レベルだが差別化スコア{differentiation_score}/10で類似性あり"
                }
                recorded_intents.append(recorded_intent)
    
    # トラッカーに追加
    if new_int_candidates:
        tracker.setdefault('pending_high_intent_keywords', []).extend(new_int_candidates)
    
    if recorded_intents:
        tracker.setdefault('analyzed_intents', []).extend(recorded_intents)
    
    # ファイル保存
    with open('intent_tracker.json', 'w', encoding='utf-8') as f:
        json.dump(tracker, f, ensure_ascii=False, indent=2)
    
    return {
        "original_keyword": original_keyword,
        "new_int_candidates": new_int_candidates,
        "recorded_intents": recorded_intents,
        "total_sub_intents": len(sub_intents),
        "message": f"抽出されたサブ意図: {len(sub_intents)}件、新規INT候補: {len(new_int_candidates)}件、記録のみ: {len(recorded_intents)}件"
    }

def calculate_differentiation_score(sub_intent: Dict, existing_intents: List[Dict]) -> int:
    """差別化スコアを計算"""
    if not existing_intents:
        return 10
    
    score = 10
    
    for existing in existing_intents:
        # 意図タイプの重複チェック
        if existing.get('intent_type') == sub_intent['intent_type']:
            score -= 3
        
        # 対象読者の重複チェック
        if existing.get('target_audience') == sub_intent['target_audience']:
            score -= 2
        
        # キーワードの類似性チェック
        sub_words = set(sub_intent['suggested_keyword'].split())
        existing_words = set(existing.get('keyword', '').split())
        overlap = len(sub_words & existing_words)
        if overlap >= 2:
            score -= 3
        elif overlap == 1:
            score -= 1
    
    return max(1, score)

# テスト実行用
if __name__ == "__main__":
    # サンプル分析結果
    sample_analysis = """
    ## Combined Keyword Analysis Table
    | 複合キーワード | 概念・話題 | 意図カテゴリ | 判定理由 |
    |---|---|---|---|
    | 生成AI + 定型業務 + 自動化 | 業務効率化・DX推進 | Informational + Commercial Investigation | 具体的な導入方法を求める |

    ## Combined-Intent Summary
    - メイン意図: 定型業務を自動化して効率化したい
    - AI導入時のセキュリティ・リスク管理が心配で対策方法を知りたい
    - 中小企業でも導入可能なコスト効果の高いソリューションを比較検討したい
    - 従業員のスキル変化・雇用への影響を理解したい
    - 競合他社の導入状況・事例を参考にしたい
    """
    
    result = process_multi_intent_analysis("生成AI 定型業務 自動化", sample_analysis)
    print("=== 複数意図抽出テスト ===")
    print(f"結果: {result['message']}")
    print(f"新規INT候補: {len(result['new_int_candidates'])}件")
    for candidate in result['new_int_candidates']:
        print(f"  {candidate['assigned_int']}: {candidate['keyword']} ({candidate['intent_type']})")