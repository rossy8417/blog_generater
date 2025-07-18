# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a comprehensive WordPress blog article generation and management system that automates the entire content creation pipeline from search intent analysis to publication. The system uses AI-powered content generation, image creation, and automated WordPress publishing.

## Core Architecture

### Template-Driven Content Generation
The system supports two distinct content creation patterns:

#### **SEO Optimization Pattern** (keyword-based articles)
- **templates/**: Contains prompt templates for each phase of content creation
  - `intent.md`: Search intent analysis
  - `division.md`: Intent variation splitting
  - `outline.md`: Article structure planning
  - `writing.md`: Chapter-by-chapter content creation
  - `lead.md` / `summary.md`: Introduction/conclusion generation
  - `eyecatch.md` / `thumbnail.md`: Image generation prompts

#### **Story Quality Pattern** (theme-based articles)
- **Story Templates**: Focus on narrative engagement and intellectual curiosity
  - `story_outline_template.md`: Creates engaging, narrative-driven article structures
  - `story_writing_template.md`: Generates compelling, story-focused chapter content
  - Emphasizes readability, emotional connection, and thought-provoking perspectives
  - Optimizes for reader engagement over search engine optimization

### Multi-Phase Content Pipeline

#### **SEO Optimization Pipeline**
1. **Intent Analysis**: Analyze search keywords and identify multiple user intents (INT-01, INT-02, etc.)
2. **Content Planning**: Create structured outlines with SEO optimization
3. **Content Creation**: Generate 6-chapter articles using AI templates
4. **Image Generation**: Create eyecatch images (OpenAI gpt-image-1) and thumbnails (Google Imagen 3)
5. **WordPress Publishing**: Automated posting with Gutenberg block formatting

#### **Story Quality Pipeline**
1. **Theme Development**: Direct theme-to-outline creation using story templates
2. **Narrative Planning**: Structure engaging, story-driven content with `story_outline_template.md`
3. **Story Creation**: Generate compelling 6-chapter narratives using `story_writing_template.md`
4. **Visual Storytelling**: Create thematic images that support narrative elements
5. **Gutenberg Integration**: Convert story content to WordPress blocks while preserving engagement elements

### File Organization System
- **outputs/**: Final deliverables organized as `{title}-INT-{number}/`
  - `complete_article.md`: Final article content
  - `metadata.json`: Article metadata
  - `*eyecatch*.jpg`: Main article image
  - `*chapter*.jpg`: Chapter-specific images
- **tmp/**: Temporary working files and development artifacts
- **scripts/**: Main execution scripts
- **utils/**: Shared utilities and managers

## Essential Commands

### Environment Setup
```bash
pip install -r requirements.txt
```

Required environment variables in `.env`:
```
GOOGLE_API_KEY=your_gemini_api_key        # Imagen 3 image generation
OPENAI_API_KEY=your_openai_api_key        # gpt-image-1 image generation
WORDPRESS_API_KEY=your_wordpress_api_key  # WordPress posting/updating
WORDPRESS_ENDPOINT=your_wordpress_url     # WordPress API URL
```

### Content Creation Commands

#### Generate Images
```bash
# Generate eyecatch image only
python scripts/image_generator.py --outline outputs/article-name/outline.md --mode eyecatch

# Generate all images (eyecatch + chapter thumbnails)
python scripts/image_generator.py --outline outputs/article-name/outline.md --mode all
```

#### Publish to WordPress
```bash
# Automatically find and publish latest article with Gutenberg block conversion
python scripts/post_blog_universal.py
```

**Note**: `post_blog_universal.py` automatically handles:
- Markdown to Gutenberg block conversion for both SEO and Story patterns
- Chapter image insertion after H2 headings
- Proper heading structure validation (H2-H4 hierarchy)
- SEO elements preservation (tables, FAQ sections, checklists)

#### Update Existing Articles
```bash
# Update specific article by ID
python scripts/wordpress_update_client.py --post-id 1388 --update-content

# Update eyecatch image
python scripts/update_eyecatch_simple.py 1388
```

**⚠️ IMPORTANT**: WordPress APIエンドポイントのガイドライン
- すべてのWordPress API呼び出しで.envのWORDPRESS_ENDPOINTを使用
- 標準REST API使用時: `WORDPRESS_ENDPOINT`から`/wp-json/blog-generator/v1`を除去
- カスタムAPI使用時: `WORDPRESS_ENDPOINT`をそのまま使用
- ハードコードされたURL（www.ht-sw.tech等）は絶対に使用禁止

### File Management Commands

#### Organize Scattered Files
Use the magic keyword "整理整頓" in Claude Code or:
```bash
python scripts/organize_outputs.py
```

#### Clean Outputs Directory
Use the magic keyword "バルス" in Claude Code to completely clear outputs/

## Key System Components

### OutputManager (utils/output_manager.py)
Handles automatic file organization and metadata extraction. Ensures all generated content is properly categorized in the `outputs/{title}-INT-{number}/` structure.

### WordPress Integration (scripts/wordpress_client.py)
- Converts Markdown to Gutenberg blocks
- Handles image uploads and chapter-specific image insertion
- Manages WordPress post creation and updates
- Supports both draft and published post states

### Image Generation System (scripts/image_generator.py)
- **Eyecatch**: Uses OpenAI gpt-image-1 for Japanese text-embedded images
- **Thumbnails**: Uses Google Imagen 3 for chapter-specific visuals
- Automatic image optimization (95% size reduction for eyecatch images)
- Progressive JPEG conversion with transparency handling

### Multi-Intent Tracking (config/intent_variation_tracker.json)
Tracks different search intents for the same base keywords, enabling creation of multiple targeted articles for different audience segments.

## Content Quality Standards

### SEO Requirements
- H2-H4 heading hierarchy only (H5+ prohibited)
- 20,000+ character articles with 6 chapters
- Keyword optimization in headings and content
- Meta descriptions under 120 characters

### Content Structure
- Title with emotional triggers and numbers
- Introduction with problem/solution framework
- 6 chapters with specific H2 headings
- Conclusion with clear CTA
- Chapter images inserted after H2 headings

### Image Standards
- Eyecatch: 500KB or less, optimized JPEG
- Thumbnails: 800KB or less per chapter
- Automatic WordPress media library integration

## Multi-Agent Workflow with Validation Integration

The system operates with a sophisticated 4-agent collaboration model through tmux sessions, now enhanced with automated heading structure validation at multiple checkpoints:

### Agent Hierarchy and Communication
- **President0 (Claude Code session)**: Strategic oversight, business vision, and quality standards enforcement
- **Boss1**: Project coordination, task distribution, and team facilitation
- **Worker1, Worker2, Worker3**: Specialized execution agents with specific responsibilities

### Detailed Agent Roles

#### President0 (Strategic Command)
- **Vision Setting**: Analyzes user requirements and sets strategic direction
- **Quality Enforcement**: Ensures 100% compliance with content standards (H5 tag prohibition, 20,000+ characters, 6 chapters)
- **System Integration**: Coordinates all README.md functions and template strategies
- **Communication**: Sends instructions to Boss1 via tmux using `./Claude-Code-Blog-communication/agent-send.sh boss1 "instructions"`

#### Boss1 (Project Management)
- **Strategic Execution**: Translates President0's vision into actionable project plans
- **Phase Management**: Orchestrates 3-phase workflow (Planning → Content → Publishing)
- **Quality Control**: Implements rigorous verification systems and monitoring
- **Worker Coordination**: Manages parallel execution and progress tracking

#### Worker1 (Content & Eyecatch Specialist)
- **Phase2**: First-half content creation (Chapters 1-2)
- **Phase3**: Eyecatch image generation using OpenAI gpt-image-1
- **Focus**: E-A-T enhancement, professional expertise, and visual branding

#### Worker2 (Content & Thumbnails Specialist)  
- **Phase2**: Middle content creation (Chapters 3-4)
- **Phase3**: Chapter thumbnail generation (Chapters 1-3) using Google Imagen 3
- **Focus**: Engagement optimization, practical solutions, and visual storytelling

#### Worker3 (Content & Thumbnails Specialist)
- **Phase2**: Final content creation (Chapters 5-6)
- **Phase3**: Chapter thumbnail generation (Chapters 4-6) using Google Imagen 3
- **Focus**: Implementation guidance, CTA optimization, and conclusion strength

### Workflow Execution Model

#### Phase 1: Strategic Planning (Boss1 Solo)
1. **Search Intent Analysis**: Using templates/intent.md for keyword analysis
2. **Intent Division**: Creating INT-numbered variations with templates/division.md
3. **Outline Creation**: SEO-optimized structure with templates/outline.md

#### Phase 2: Parallel Content Creation with Validation
- **Parallel Execution**: All 3 workers simultaneously create their assigned chapters
- **Quality Monitoring**: Real-time verification of H5 tag prohibition, character counts, E-A-T elements
- **Heading Structure Validation**: Each worker validates chapter content using `scripts/validate_article.py`
- **Boss Integration**: Boss1 handles lead/summary creation and final article integration with validation

#### Phase 3: Parallel Image Generation & Publishing with Final Validation
- **Parallel Image Creation**: Workers generate eyecatch and chapter-specific thumbnails
- **Optimization Pipeline**: Automatic 95% size reduction and format optimization
- **Pre-Publishing Validation**: Final heading structure check before WordPress posting
- **WordPress Integration**: Automated posting with Gutenberg block formatting

### Communication Protocols
- **Command Structure**: President0 → Boss1 → Workers
- **Progress Reporting**: Workers → Boss1 → President0
- **Quality Verification**: Multi-level checks at each phase transition
- **Error Handling**: Automatic retry systems and alternative execution paths

## File Naming Conventions

- Articles: `{title}-INT-{number}/complete_article.md`
- Images: `*eyecatch*.jpg`, `*chapter{n}*.jpg`
- Metadata: `metadata.json` in each article directory
- Backups: Timestamped with format `YYYYMMDD_HHMMSS`

## WordPress Integration Notes

### Article Publishing Process
- All articles are posted as drafts by default
- Chapter images are automatically inserted after numbered H2 headings
- Meta Description and local image paths are automatically removed from content
- Supports both new post creation and existing post updates
- Maintains detailed logging in `logs/send_log.txt`

### Gutenberg Block Editor Conversion
The system provides comprehensive Markdown to WordPress Gutenberg block conversion via `scripts/wordpress_client.py`:

#### **Block Conversion Features**
- **Heading Structure**: Maintains proper H2-H4 hierarchy with automatic H5/H6 prohibition
- **Content Blocks**: Converts paragraphs, lists, tables, quotes, and code blocks
- **Image Integration**: Transforms Markdown images to WordPress image blocks with proper metadata
- **Chapter Images**: Automatically inserts chapter-specific thumbnails after H2 headings
- **Typography**: Applies WordPress block classes (`wp-block-heading`, `wp-block-image`, etc.)

#### **SEO Template Integration**
Traditional SEO optimization pattern (`intent.md → division.md → outline.md → writing.md`) includes comprehensive block conversion:
- **Content Processing**: Markdown content from `writing.md` template automatically converts to Gutenberg blocks
- **SEO Elements**: FAQ sections, tables, checklists maintain structure during conversion
- **Visual Enhancements**: Emoji indicators (💡, ⚠️, 🎯, 📊) and formatting preserved
- **Chapter Structure**: H2 headers trigger automatic thumbnail insertion for visual appeal

#### **Story Template Integration**
Both SEO and Story patterns utilize the same robust block conversion process:
- **Story Content**: Narrative-driven content from `story_writing_template.md` converts seamlessly
- **Engagement Elements**: Emoji indicators (💡, 📝, 🤔) and visual callouts preserved
- **Reading Flow**: Proper paragraph breaks and section divisions maintained
- **Interactive Elements**: Questions and thought-provokers formatted as engaging content blocks

#### **Quality Assurance**
- **Pre-conversion Validation**: Heading structure verification before WordPress posting
- **Block Verification**: Automatic confirmation of proper Gutenberg block generation
- **Image Insertion Check**: Verification that chapter images appear after correct H2 headings
- **Content Integrity**: Ensures story elements and formatting are preserved during conversion

## Heading Structure Validation System

### Automated Prevention of Heading Structure Errors

The system includes comprehensive validation tools to prevent heading structure issues:

#### Pre-posting Validation
```bash
# Validate article before posting
python scripts/validate_article.py outputs/article-name/complete_article.md
```

#### Built-in Validation Rules
- **H5/H6 Prohibition**: Automatically detects and prevents H5/H6 usage
- **Template ID Detection**: Identifies remaining template identifiers (H3-1, etc.)
- **Heading Hierarchy Check**: Ensures proper H2→H3→H4 structure
- **WordPress Conversion Validation**: Verifies correct Gutenberg block generation

#### Validation Commands
```bash
# Pre-posting validation (recommended)
python scripts/validate_article.py outputs/article-name/complete_article.md

# Direct heading validator
python scripts/heading_validator.py complete_article.md

# WordPress posting with automatic validation
python scripts/post_blog_universal.py  # Now includes built-in validation
```

#### Validation Output
- ✅ **Success**: Article structure is correct and ready for posting
- ⚠️ **Warning**: Minor issues detected, posting continues with notification
- ❌ **Error**: Critical issues found, posting halted until resolution

## Article Update and Rewrite Safety Guidelines

### Interactive Update Confirmation System

**When rewrite instructions are given, Claude Code MUST confirm the following with the user:**

#### 1. **Content Update Scope Confirmation**
```
記事ID [ID] のリライトを開始します。以下を確認してください：

📝 **更新内容**:
- [ ] 記事本文のリライト
- [ ] 見出し構造の最適化
- [ ] SEO要素の改善

🖼️ **画像更新の有無**:
- [ ] アイキャッチ画像の差し替えあり
- [ ] 章別画像の差し替えあり  
- [ ] 画像更新なし（既存画像維持）

🔍 **ファクトチェック実施**:
- [ ] 最新情報への更新が必要
- [ ] 技術仕様の正確性確認が必要
- [ ] ファクトチェック不要

上記の確認後、処理を開始します。画像更新がある場合は、適切な差し替え処理を並行実行します。
```

#### 2. **Image Update Integration Protocol**
When image updates are confirmed:
- Execute `scripts/image_update_manager.py` for systematic image replacement
- Maintain image version history for rollback capability
- Verify image optimization and WordPress compatibility
- Update chapter image insertion automatically

#### 3. **Fact-Check Integration Protocol**
When fact-checking is confirmed:
- Execute multi-agent fact-checking via Worker1-3 assignment
- Verify technical specifications, statistics, and legal information
- Generate `factcheck_report_worker*.md` files for transparency
- Apply corrections before final WordPress update

### Critical Safety Protocols for Article Updates

When performing article updates or rewrites, the system enforces strict safety protocols to prevent accidental content loss or unintended new post creation:

#### Pre-Update Validation
```bash
# Always verify article exists before updating
python scripts/wordpress_update_client.py --post-id {ID} --check-only

# For rewrite operations, verify target article
python -c "
import requests, os
from dotenv import load_dotenv
load_dotenv()
response = requests.get(f'{os.getenv(\"WORDPRESS_ENDPOINT\")}/get-post/{POST_ID}', 
                       headers={'X-API-Key': os.getenv('WORDPRESS_API_KEY')})
if response.status_code != 200:
    print('❌ Article not found - ABORTING UPDATE')
    exit(1)
print(f'✅ Article found: {response.json().get(\"title\")}')
"
```

#### Update Safety Rules
1. **Mandatory Existence Check**: All update operations MUST verify article existence before proceeding
2. **Automatic Abort on 404**: If target article is not found, processing stops immediately
3. **No Fallback Creation**: Update operations NEVER create new posts when target is missing
4. **Backup Before Update**: System automatically creates backup before any content modification
5. **Rollback Capability**: Failed updates can be reverted using backup restoration

#### Error Handling for Updates
- **PostNotFoundError**: Thrown when target article doesn't exist - processing halts
- **InsufficientPermissionError**: Thrown for permission issues - processing halts  
- **UpdateConflictError**: Thrown for concurrent modification conflicts - processing halts
- **Graceful Degradation**: Any update failure preserves original content integrity

#### Safe Update Commands
```bash
# Article content update with safety checks
python scripts/wordpress_update_client.py --post-id {ID} --update-content

# Eyecatch update with validation
python scripts/update_eyecatch_simple.py {ID}

# Chapter image updates with verification
python scripts/image_update_manager.py --post-id {ID} --mode chapter
```

#### Prohibited Operations During Updates
- Creating new posts when update target is missing
- Bypassing existence validation checks
- Forcing updates without backup creation
- Ignoring API error responses (404, 403, 409)

## Multi-Agent Workflow Monitoring System

### President0 Monitoring and Continuity Management

The system includes automated monitoring to prevent work stagnation and ensure continuous progress:

#### Continuous Work Protocol
1. **No Work Interruption**: All phases (Phase1→Phase2→Phase3) must execute continuously
2. **Automatic Phase Transition**: Each phase automatically starts the next upon completion
3. **Active Monitoring**: 30-minute interval checks for Boss1 activity
4. **Automatic Escalation**: Immediate prompting when inactivity is detected

#### Monitoring System Commands
```bash
# Start President0 monitoring system
./Claude-Code-Blog-communication/monitoring_system.sh &

# Manual Boss1 activity check
tail -f logs/send_log.txt | grep "boss1: SENT"

# Emergency Boss1 reactivation
./Claude-Code-Blog-communication/agent-send.sh boss1 "President0緊急指示: 作業継続確認"
```

#### Work Continuity Rules
- **5-minute intervals**: Worker progress checks during active phases
- **15-minute threshold**: Emergency prompting for non-responsive agents
- **30-minute threshold**: Automatic work redistribution
- **No stopping between phases**: Continuous execution until final completion

#### Quality Assurance During Continuous Work
- Real-time heading structure validation
- Automatic file organization and backup
- Progress reporting every 30 minutes
- Error detection with immediate correction protocols
## Boss1報告ログ自動管理システム（President0実装）

### 🧹 ログクリーンアップ機能
President0により、Boss1報告ログの蓄積問題を解決する自動管理システムを実装

#### 緊急クリーンアップコマンド
```bash
# 即座にログクリーンアップ実行（20KB超過ログを2KB以下に削減）
python3 -c "
import os, shutil, datetime
from pathlib import Path
message_queue_dir = Path('tmp/message_queue')
backup_dir = Path('tmp/log_backups')
backup_dir.mkdir(parents=True, exist_ok=True)
for log_file in message_queue_dir.glob('*_queue.log'):
    size_kb = log_file.stat().st_size / 1024
    if size_kb > 20:
        backup_path = backup_dir / f'{log_file.stem}_backup_{datetime.datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.log'
        shutil.copy2(log_file, backup_path)
        with open(log_file, 'r', encoding='utf-8') as f: lines = f.readlines()
        with open(log_file, 'w', encoding='utf-8') as f: f.writelines(lines[-50:])
        print(f'✅ {log_file.name}: {size_kb:.1f}KB → {log_file.stat().st_size/1024:.1f}KB')
"
```

#### 定期自動クリーンアップ
```bash
# 定期実行スクリプト実行
./scripts/auto_log_cleanup.sh

# バックグラウンド定期実行設定（1時間毎）
# crontab -e で以下を追加:
# 0 * * * * ./scripts/auto_log_cleanup.sh >> logs/cleanup.log 2>&1
```

### 📊 ログ管理ルール
- **サイズ制限**: 各ログファイル20KB以下維持
- **保持ライン数**: 最新50エントリのみ保持
- **バックアップ**: クリーンアップ前に自動バックアップ作成
- **バックアップ保持期間**: 7日間（自動削除）

### 🔧 トラブルシューティング
#### Boss1報告遅延時の対処
1. ログサイズ確認: `du -h tmp/message_queue/*.log`
2. 緊急クリーンアップ実行: 上記コマンド実行
3. 接続確認再実行: 「接続確認」合言葉実行

#### 効果
- boss1_queue.log: 35.9KB → 2.0KB（94%削減）
- president_queue.log: 21.7KB → 2.1KB（90%削減）
- 報告システム応答性能大幅改善

EOF < /dev/null

## 完全正常状態永続化システム（President0実装）

### 🎯 Boss1ターミナル落ち対策・完全復旧システム
President0により、Boss1ターミナル落ちによる双方向通信遮断問題の根本解決システムを実装

#### 緊急復旧コマンド（最重要）
```bash
# Boss1ターミナル落ち時の緊急復旧
./scripts/emergency_connection_recovery.sh

# システムヘルスチェック
./scripts/emergency_connection_recovery.sh --health-check

# 高度な状態管理（Python版）
python3 scripts/connection_state_manager.py
```

#### 📋 緊急復旧システムの動作
1. **multiagentセッション完全再作成**: 破損したセッションをクリーン環境で再構築
2. **全ペインClaude Code起動**: Boss1-Worker1,2,3で確実な起動実行
3. **President0→Boss1接続確認**: 指揮系統の基盤確認
4. **Boss1→Worker双方向接続確認**: Worker1,2,3との完全な双方向通信確認

#### 🛡️ 予防・監視機能
```bash
# 定期ヘルスチェック（crontab推奨）
*/30 * * * * /mnt/c/home/hiroshi/blog_generator/scripts/emergency_connection_recovery.sh --health-check

# 継続監視ログ確認
tail -f logs/connection_recovery.log
```

### 🔧 トラブルシューティング手順

#### Boss1ターミナル落ち症状
- Boss1からの応答が突然停止
- Worker1,2,3への指示が届かない
- 「接続確認」合言葉が無効

#### 対処手順（優先順）
1. **緊急復旧実行**: `./scripts/emergency_connection_recovery.sh`
2. **ヘルスチェック**: 復旧後の状態確認
3. **接続確認合言葉**: 最終確認として実行

#### 根本原因と対策
- **原因**: Boss1ペインのClaude Code突然終了
- **対策**: セッション完全再作成 + 全ペイン再起動
- **予防**: 定期ヘルスチェック + 自動復旧システム

### 📊 完全正常状態の定義
President0が定義する理想的なシステム状態：

#### TMUXセッション構造
```
multiagent:0.0 (Boss1)   - Claude Code稼働中
multiagent:0.1 (Worker1) - Claude Code稼働中  
multiagent:0.2 (Worker2) - Claude Code稼働中
multiagent:0.3 (Worker3) - Claude Code稼働中
president:0.0 (President0) - Claude Code稼働中
```

#### 通信フロー確認
- ✅ President0→Boss1: 指示送信成功
- ✅ Boss1→Worker1,2,3: 並行指示送信成功
- ✅ Worker1,2,3→Boss1: 応答受信成功
- ✅ Boss1→President0: 統合報告成功

### 🚀 運用ベストプラクティス

#### 日常運用
1. **プロジェクト開始前**: `--health-check`で状態確認
2. **異常検知時**: 即座に緊急復旧実行
3. **定期メンテナンス**: 週1回の完全復旧実行

#### システム管理
- **ログ監視**: `logs/connection_recovery.log`の定期確認
- **状態保存**: `tmp/connection_state.json`での状態追跡
- **バックアップ**: 正常状態でのセッション構成保存

#### エスカレーション
緊急復旧でも解決しない場合：
1. TMUXセッション全削除・再作成
2. Claude Codeプロセス完全再起動
3. システム全体の再起動検討

EOF < /dev/null
