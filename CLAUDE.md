# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a comprehensive WordPress blog article generation and management system that automates the entire content creation pipeline from search intent analysis to publication. The system uses AI-powered content generation, image creation, and automated WordPress publishing.

## Core Architecture

### Template-Driven Content Generation
- **templates/**: Contains prompt templates for each phase of content creation
  - `intent.md`: Search intent analysis
  - `division.md`: Intent variation splitting
  - `outline.md`: Article structure planning
  - `writing.md`: Chapter-by-chapter content creation
  - `lead.md` / `summary.md`: Introduction/conclusion generation
  - `eyecatch.md` / `thumbnail.md`: Image generation prompts

### Multi-Phase Content Pipeline
1. **Intent Analysis**: Analyze search keywords and identify multiple user intents (INT-01, INT-02, etc.)
2. **Content Planning**: Create structured outlines with SEO optimization
3. **Content Creation**: Generate 6-chapter articles using AI templates
4. **Image Generation**: Create eyecatch images (OpenAI gpt-image-1) and thumbnails (Google Imagen 3)
5. **WordPress Publishing**: Automated posting with Gutenberg block formatting

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
# Automatically find and publish latest article
python scripts/post_blog_universal.py
```

#### Update Existing Articles
```bash
# Update specific article by ID
python scripts/wordpress_update_client.py --post-id 1388 --update-content

# Update eyecatch image
python scripts/update_eyecatch_simple.py --post-id 1388
```

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
- **Communication**: Sends instructions to Boss1 via tmux using `./agent-send.sh boss1 "instructions"`

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

- All articles are posted as drafts by default
- Chapter images are automatically inserted after numbered H2 headings
- Meta Description and local image paths are automatically removed from content
- Supports both new post creation and existing post updates
- Maintains detailed logging in `logs/send_log.txt`

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
./monitoring_system.sh &

# Manual Boss1 activity check
tail -f logs/send_log.txt | grep "boss1: SENT"

# Emergency Boss1 reactivation
./agent-send.sh boss1 "President0緊急指示: 作業継続確認"
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