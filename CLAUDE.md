# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a comprehensive WordPress blog article generation and management system that automates the entire content creation pipeline from search intent analysis to publication. The system uses AI-powered content generation, image creation, and automated WordPress publishing.

## Core Architecture

### Template-Driven Content Generation
The system supports two distinct content creation patterns:

#### **SEO Optimization Pattern** (keyword-based articles)
- **Hybrid Template System**: AI-optimized YAML + Human-readable Markdown
  - `config/intent_analysis_template.yaml`: Advanced search intent analysis with morphological framework
  - `config/intent_division_template.yaml`: Intent variation splitting (JSON extraction)
  - `config/outline_strategy_template.yaml`: CTR-optimized article structure planning
  - `config/content_generation_template.yaml`: SEO-optimized chapter creation
  - `config/lead_generation_template.yaml` / `config/summary_generation_template.yaml`: Introduction/conclusion generation
  - `config/eyecatch_generation_template.yaml` / `config/thumbnail_generation_template.yaml`: Image generation

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
- **outputs/**: Final deliverables and completed projects
  - `final_articles/{title}-INT-{number}/`: Published articles
    - `complete_article.md`: Final article content
    - `metadata.json`: Article metadata
    - `*eyecatch*.jpg`: Main article image
    - `*chapter*.jpg`: Chapter-specific images
  - `current_work/`: Active project files
  - `archives/`: Completed project reports and historical data
- **tmp/**: Temporary working files categorized by function
  - `agent_work/`: Multi-agent collaboration files
  - `quality_checks/`: Validation and testing files
  - `temporary_files/`: Short-term processing files
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
# 統合画像管理システム（推奨）
# Generate eyecatch image only
python scripts/consolidated_image_manager.py generate --outline outputs/article-name/outline.md --mode eyecatch

# Generate all images (eyecatch + chapter thumbnails)
python scripts/consolidated_image_manager.py generate --outline outputs/article-name/outline.md --mode all

# レガシー版も利用可能（後方互換性）
python scripts/image_generator.py --outline outputs/article-name/outline.md --mode eyecatch
python scripts/image_generator.py --outline outputs/article-name/outline.md --mode all
```

#### Publish to WordPress
```bash
# WordPress投稿（品質チェック統合版）- 推奨
python scripts/post_blog_universal.py
```

**Note**: `post_blog_universal.py` now includes comprehensive quality check features:
- **Pre-publishing Quality Check**: Comprehensive article validation before WordPress posting
- **Automatic Fixes**: Auto-correction of common quality issues
- **H5/H6 Tag Prevention**: Strict enforcement of heading hierarchy rules
- **Template ID Detection**: Removal of remaining template identifiers
- **Content Structure Validation**: Verification of proper chapter organization
- **WordPress Conversion Validation**: Gutenberg block generation verification
- **Detailed Quality Reports**: Complete quality assessment with fix recommendations

The post_blog_universal.py has been enhanced to include all quality check functionalities for seamless and safe WordPress publishing.

Standard features (both versions):
- Markdown to Gutenberg block conversion for both SEO and Story patterns
- Chapter image insertion after H2 headings
- Proper heading structure validation (H2-H4 hierarchy)
- SEO elements preservation (tables, FAQ sections, checklists)

#### Update Existing Articles
```bash
# Update specific article by ID
python scripts/wordpress_update_client.py --post-id 1388 --update-content

# 統合画像更新（推奨）
# Update eyecatch image
python scripts/consolidated_image_manager.py update --post-id 1388 --type eyecatch

# Update chapter images
python scripts/consolidated_image_manager.py update --post-id 1388 --type chapter --chapter-num 1

# Quick update (legacy compatibility)
python scripts/consolidated_image_manager.py quick-update 1388

# レガシー版（段階的廃止予定）
python scripts/consolidated_image_manager.py update --post-id 1388 --type eyecatch

# 簡単更新（後方互換性）
python scripts/consolidated_image_manager.py quick-update 1388

# ※ レガシーファイルは統合版へ移行済み・削除済み
# update_eyecatch_simple.py -> consolidated_image_manager.py quick-update
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

### 統合画像管理システム (scripts/consolidated_image_manager.py)
- **新規画像生成**: OpenAI gpt-image-1（アイキャッチ）・Google Imagen 3（サムネイル）
- **WordPress画像更新**: 既存記事の画像差し替え・バージョン管理
- **自動最適化**: 95%サイズ削減・Progressive JPEG変換・透明背景対応
- **後方互換性**: 従来のimage_generator.pyインターフェース維持（レガシーファイルは統合済み）
- **バージョン管理**: 画像更新履歴・復元機能

### レガシー画像システム（統合済み）
- **scripts/image_generator.py**: 基本画像生成機能（引き続き利用可能）
- **scripts/update_eyecatch_simple.py**: 簡単アイキャッチ更新 → 統合済み・削除済み
- **scripts/image_update_manager.py**: 画像バージョン管理 → 統合済み・削除済み

### Multi-Intent Tracking (config/intent_variation_tracker.json)
Tracks different search intents for the same base keywords, enabling creation of multiple targeted articles for different audience segments.

## スクリプト統合システム（2025年7月統合版）

### 統合済みスクリプト構成

#### 1. WordPress投稿関連（統合完了）
- **`post_blog_universal.py`**: 品質チェック統合版（メインスクリプト）
  - 統合機能: 品質チェック、自動修正、H5/H6タグ禁止、見出し構造検証
  - 従来の`post_blog_universal_with_quality_check.py`機能を統合
- **`wordpress_client.py`**: コアライブラリ（維持）
- **削除済み**: `post_blog_correct.py`（空ファイル）

#### 2. 品質チェック・検証関連（個別維持）
- **`pre_wordpress_quality_checker.py`**: 包括的品質チェックシステム
- **`validate_article.py`**: コマンドライン記事検証ツール
- **`heading_validator.py`**: 見出し構造専用検証ツール

#### 3. 記事更新・リライト関連（統合計画策定済み）
- **統合対象**: 
  - `interactive_rewrite_manager.py`（インタラクティブUI）
  - `article_update_manager.py`（汎用更新システム）
  - `article_rewrite_system.py`（3Phase構造）
- **統合後**: `article_rewrite_integrated.py`（計画中）
- **維持**: `wordpress_update_client.py`（コアライブラリ）
- **削除済み**: `article_rewrite_complete_system.py`（空ファイル）

#### 4. 画像管理関連（統合計画策定済み）
- **基盤**: `image_generator.py`（Imagen 3 & OpenAI gpt-image-1）
- **統合予定機能**:
  - image_update_manager.pyのバージョン管理機能（統合済み）
  - update_eyecatch_simple.pyのシンプル更新機能（統合済み）

#### 5. ファイル管理・整理関連（統合計画策定済み）
- **基盤**: `organize_outputs.py`（自動ファイル整理）
- **統合予定機能**:
  - `smart_tmp_cleanup.py`のインテリジェントクリーンアップ
  - `log_cleanup_manager.py`のログ自動管理

### 統合による改善点

#### 機能統合メリット
- **コード重複の排除**: 類似機能を統合し、保守性向上
- **一貫したインターフェース**: 統一されたコマンド体系
- **品質保証の強化**: 全スクリプトに品質チェックを統合
- **実行効率の向上**: 機能統合により処理速度向上

#### 後方互換性
- **既存コマンド維持**: 従来のコマンド構文は引き続き利用可能
- **段階的移行**: 新機能への移行は任意のタイミングで実行可能
- **エラーハンドリング**: 非互換性の自動検出と適切なエラーメッセージ

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

## Multi-Agent Communication and Workflow System

The system operates with a sophisticated 4-agent collaboration model through tmux sessions, enhanced with automated validation and seamless communication protocols:

### Agent Communication System

#### Agent Configuration
- **PRESIDENT** (separate session): Strategic oversight and quality enforcement
- **boss1** (multiagent:0.0): Team leader and project coordination
- **worker1,2,3** (multiagent:0.1-3): Specialized task execution

#### Agent Role References
- **PRESIDENT**: @Claude-Code-Blog-communication/instructions/president.yaml
- **boss1**: @Claude-Code-Blog-communication/instructions/boss.yaml
- **worker1,2,3**: @Claude-Code-Blog-communication/instructions/worker.yaml

#### Message Sending Protocol
```bash
# Working directory: /mnt/c/home/hiroshi/blog_generator
./Claude-Code-Blog-communication/agent-send.sh [target] "[message]"

# Or absolute path (recommended)
/mnt/c/home/hiroshi/blog_generator/Claude-Code-Blog-communication/agent-send.sh [target] "[message]"
```

#### Connection Verification
Each Worker can verify Boss1 connection:
```bash
/mnt/c/home/hiroshi/blog_generator/Claude-Code-Blog-communication/agent-send.sh boss1 "connection-test"
```

#### Communication Flow
PRESIDENT → boss1 → workers → boss1 → PRESIDENT

#### 🎯 Magic Command "connection-check" (Connection Recovery)
**One-command complete collaboration state restoration:**

```bash
# Use in Claude Code
connection-check

# Or direct execution via unified controller
./Claude-Code-Blog-communication/tmux-unified-controller.sh boss1 "connection-check"
```

**Automatic Execution Process:**
1. **System Foundation Repair**: TMUX and message queue initialization
2. **Boss1 Recovery**: Response testing, recovery processing, role redefinition
3. **Worker Recovery**: Individual recovery, Claude Code restart, role configuration
4. **Hierarchical Connection Test**: Complete command system verification
5. **Collaboration State Establishment**: Final confirmation and persistent recording

**Complete Autonomous Features:**
- ✅ Automatic fault detection and repair
- ✅ TMUX session automatic recreation
- ✅ Claude Code automatic restart
- ✅ Individual Worker recovery processing
- ✅ Strict hierarchical control
- ✅ State persistence recording

## Multi-Agent Workflow with Validation Integration

Enhanced 4-agent collaboration model with automated heading structure validation at multiple checkpoints:

### Agent Hierarchy and Communication
- **President0 (Claude Code session)**: Strategic oversight, business vision, and quality standards enforcement
- **Boss1**: Project coordination, task distribution, and team facilitation
- **Worker1, Worker2, Worker3**: Specialized execution agents with specific responsibilities

### 🔄 Automatic Agent Role Management System

#### **Phase0: Agent Initialization** (Automatic YAML Role Loading)
Every blog generation and article update workflow now includes automatic Phase0 initialization:
- **Boss1**: Automatically loads `@Claude-Code-Blog-communication/instructions/boss.yaml`
- **Worker1,2,3**: Automatically load `@Claude-Code-Blog-communication/instructions/worker.yaml`
- **President0**: References `@Claude-Code-Blog-communication/instructions/president.yaml`
- **Role Confirmation**: All agents confirm role understanding before proceeding to main workflow

#### **tmux Session Recovery with Auto YAML Loading**
All tmux session recovery and restart operations now include automatic YAML role loading:
- **Normal Recovery**: YAML loading integrated into 5-phase recovery process
- **Emergency Recovery**: Automatic YAML loading immediately after Claude Code startup
- **Session Creation**: New multiagent sessions automatically load YAML roles
- **Worker Recovery**: Individual worker recovery includes YAML role reloading
- **Zero Manual Intervention**: No manual role reminders needed after session restarts

#### **Periodic Role Reminder System**
Prevents agents from forgetting their roles and reporting obligations during long workflows:
- **Auto-Start**: Automatically starts with every blog/article workflow (30-minute intervals)
- **Periodic Reminders**: Regular role and reporting obligation confirmations
- **YAML Reload**: Automatic role definition reloading every 3rd reminder cycle
- **Responsiveness Check**: Continuous agent response monitoring

#### **Manual Role Reminder Commands**
```bash
# Start role reminder system manually
./Claude-Code-Blog-communication/tmux-unified-controller.sh --system role-reminder start

# Check current status
./Claude-Code-Blog-communication/tmux-unified-controller.sh --system role-reminder check

# Send manual reminder
./Claude-Code-Blog-communication/tmux-unified-controller.sh --system role-reminder manual

# Stop role reminder system
./Claude-Code-Blog-communication/tmux-unified-controller.sh --system role-reminder stop
```

### 📊 Sequential Report Collection System (Report Conflict Prevention)

#### **Problem: Report Timing Conflicts**
When multiple Workers report simultaneously to Boss1, race conditions can cause report loss or oversight.

#### **Solution: Sequential Report Collection**
Implements 15-second intervals between Worker reports to ensure all reports are received:

**Automatic Sequential Collection:**
```bash
# Collect Worker reports sequentially
./Claude-Code-Blog-communication/tmux-unified-controller.sh --system sequential-report collect-boss1

# Confirm receipt of all Worker reports
./Claude-Code-Blog-communication/tmux-unified-controller.sh --system sequential-report confirm-workers

# Analyze report conflicts
./Claude-Code-Blog-communication/tmux-unified-controller.sh --system sequential-report analyze
```

**Manual Sequential Process:**
1. **Worker1 Only**: Request report, wait 15 seconds
2. **Worker2 Only**: Request report, wait 15 seconds  
3. **Worker3 Only**: Request report, wait 15 seconds
4. **Boss1 Integration**: Create consolidated report for President0

#### **Conflict Prevention Features**
- **Sequential Timing**: 15-second intervals prevent simultaneous reports
- **Receipt Confirmation**: Verification that each report was received
- **Automatic Retry**: Failed reports are automatically retried
- **Conflict Analysis**: Detects and logs timing conflicts in message queues

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
1. **Search Intent Analysis**: Using config/intent_analysis_template.yaml for keyword analysis
2. **Intent Division**: Creating INT-numbered variations with config/intent_division_template.yaml
3. **Outline Creation**: SEO-optimized structure with config/outline_strategy_template.yaml

#### Phase 2: Parallel Content Creation with Validation
- **Parallel Execution**: All 3 workers simultaneously create their assigned chapters
- **Quality Monitoring**: Real-time verification of H5 tag prohibition, character counts, E-A-T elements
- **Heading Structure Validation**: Each worker validates chapter content using `scripts/validate_article.py`
- **Boss Integration**: Boss1 handles lead/summary creation and final article integration with validation

#### Phase 3: Parallel Image Generation & Publishing with Quality Assurance
- **Parallel Image Creation**: Workers generate eyecatch and chapter-specific thumbnails
- **Optimization Pipeline**: Automatic 95% size reduction and format optimization
- **Pre-Publishing Quality Check**: Comprehensive validation and auto-correction system
- **Quality Report Generation**: Detailed assessment with fix recommendations
- **WordPress Integration**: Automated posting with verified Gutenberg block formatting

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

## WordPress投稿前品質チェック・自動修正システム

### Comprehensive Pre-Publishing Quality Assurance

The system includes a sophisticated quality check and auto-correction system that validates articles before WordPress publishing:

#### Quality Check Features
```bash
# Run comprehensive quality check before publishing
python scripts/pre_wordpress_quality_checker.py outputs/article-name/complete_article.md

# Publish with integrated quality check (recommended - post_blog_universal.pyに統合済み)
python scripts/post_blog_universal.py
```

#### Automated Quality Checks
- **Heading Structure Validation**: Enforces H2-H4 hierarchy, prevents H5/H6 usage
- **Template ID Removal**: Detects and removes template identifiers (H3-1, etc.)
- **Content Structure Verification**: Validates chapter organization and completeness
- **WordPress Conversion Check**: Ensures proper Gutenberg block generation
- **SEO Elements Validation**: Confirms meta descriptions, title optimization
- **Image Integration Verification**: Validates chapter image placement

#### Automatic Fixes Applied
- **Template ID Cleanup**: Converts template identifiers to proper headings
- **Heading Level Correction**: Downgrades H5/H6 to H4 with styling preservation
- **Content Structure Repair**: Fixes malformed chapter organization
- **Markdown Cleanup**: Removes invalid formatting and fixes syntax issues
- **SEO Optimization**: Auto-generates missing meta descriptions

#### Quality Report Generation
- **Detailed Assessment**: Comprehensive quality score with specific issue identification
- **Fix Recommendations**: Actionable suggestions for remaining issues
- **Compliance Verification**: Confirmation of WordPress posting readiness
- **Quality History**: Tracking of improvements and issue resolution

## Heading Structure Validation System (Legacy)

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
Starting rewrite for Article ID [ID]. Please confirm the following:

📝 **Update Content**:
- [ ] Article content rewrite
- [ ] Heading structure optimization
- [ ] SEO element improvements

🖼️ **Image Update Requirements**:
- [ ] Eyecatch image replacement required
- [ ] Chapter image replacement required  
- [ ] No image updates (maintain existing images)

🔍 **Fact-checking Implementation**:
- [ ] Latest information updates required
- [ ] Technical specification accuracy verification required
- [ ] No fact-checking required

Processing will begin after confirmation. If image updates are required, appropriate replacement processing will run in parallel.
```

#### 2. **Image Update Integration Protocol**
When image updates are confirmed:
- Execute `scripts/consolidated_image_manager.py` for unified image management
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
./Claude-Code-Blog-communication/agent-send.sh boss1 "President0 Emergency Instruction: Work Continuation Confirmation"
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
## Boss1 Report Log Automatic Management System (President0 Implementation)

### 🧹 Log Cleanup Features
Automatic management system implemented by President0 to resolve Boss1 report log accumulation issues

#### Emergency Cleanup Commands
```bash
# Execute immediate log cleanup (reduce logs over 20KB to under 2KB)
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

#### Scheduled Automatic Cleanup
```bash
# Execute scheduled cleanup script
./scripts/auto_log_cleanup.sh

# Background scheduled execution setup (hourly)
# Add to crontab -e:
# 0 * * * * ./scripts/auto_log_cleanup.sh >> logs/cleanup.log 2>&1
```

### 📊 Log Management Rules
- **Size Limit**: Maintain each log file under 20KB
- **Line Retention**: Keep only latest 50 entries
- **Backup**: Create automatic backup before cleanup
- **Backup Retention**: 7 days (automatic deletion)

### 🔧 Troubleshooting
#### Response to Boss1 Report Delays
1. Check log size: `du -h tmp/message_queue/*.log`
2. Execute emergency cleanup: Run above commands
3. Re-execute connection check: Run "connection-check" magic word

#### Results
- boss1_queue.log: 35.9KB → 2.0KB (94% reduction)
- president_queue.log: 21.7KB → 2.1KB (90% reduction)
- Significant improvement in report system responsiveness

EOF < /dev/null

## Complete Normal State Persistence System (President0 Implementation)

### 🎯 Boss1 Terminal Crash Recovery - Complete Recovery System
President0 implements root solution system for bidirectional communication disruption caused by Boss1 terminal crashes

#### Emergency Recovery Commands (Critical)
```bash
# Emergency recovery for Boss1 terminal crashes
./scripts/emergency_connection_recovery.sh

# System health check
./scripts/emergency_connection_recovery.sh --health-check

# Advanced state management (Python version)
python3 scripts/connection_state_manager.py
```

#### 📋 Emergency Recovery System Operations
1. **Complete multiagent session recreation**: Rebuild corrupted sessions in clean environment
2. **All pane Claude Code startup**: Reliable startup execution for Boss1-Worker1,2,3
3. **President0→Boss1 connection verification**: Command structure foundation confirmation
4. **Boss1→Worker bidirectional connection verification**: Complete bidirectional communication verification with Worker1,2,3

#### 🛡️ Prevention and Monitoring Features
```bash
# Regular health check (crontab recommended)
*/30 * * * * /mnt/c/home/hiroshi/blog_generator/scripts/emergency_connection_recovery.sh --health-check

# Continuous monitoring log verification
tail -f logs/connection_recovery.log
```

### 🔧 Troubleshooting Procedures

#### Boss1 Terminal Crash Symptoms
- Boss1 responses suddenly stop
- Instructions to Worker1,2,3 don't reach
- "connection-check" magic word becomes invalid

#### Resolution Steps (Priority Order)
1. **Execute emergency recovery**: `./scripts/emergency_connection_recovery.sh`
2. **Health check**: Verify post-recovery status
3. **Connection check magic word**: Execute as final confirmation

#### Root Cause and Solutions
- **Cause**: Sudden termination of Claude Code in Boss1 pane
- **Solution**: Complete session recreation + all pane restart
- **Prevention**: Regular health checks + automatic recovery system

### 📊 Definition of Complete Normal State
Ideal system state as defined by President0:

#### TMUX Session Structure
```
multiagent:0.0 (Boss1)   - Claude Code running
multiagent:0.1 (Worker1) - Claude Code running  
multiagent:0.2 (Worker2) - Claude Code running
multiagent:0.3 (Worker3) - Claude Code running
president:0.0 (President0) - Claude Code running
```

#### Communication Flow Verification
- ✅ President0→Boss1: Instruction transmission success
- ✅ Boss1→Worker1,2,3: Parallel instruction transmission success
- ✅ Worker1,2,3→Boss1: Response reception success
- ✅ Boss1→President0: Integrated report success

### 🚀 Operational Best Practices

#### Daily Operations
1. **Before project start**: Verify status with `--health-check`
2. **When anomaly detected**: Execute emergency recovery immediately
3. **Regular maintenance**: Execute complete recovery weekly

#### System Management
- **Log monitoring**: Regular verification of `logs/connection_recovery.log`
- **State saving**: State tracking with `tmp/connection_state.json`
- **Backup**: Save session configuration in normal state

#### Escalation
When emergency recovery doesn't resolve:
1. Delete and recreate all TMUX sessions
2. Complete restart of Claude Code processes
3. Consider full system restart

EOF < /dev/null
