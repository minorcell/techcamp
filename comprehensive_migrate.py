#!/usr/bin/env python3
"""
Comprehensive migration script for 2025 articles to Docusaurus blog
- Migrates all articles from 2025/ to website/blog/
- Translates Chinese titles/slugs to English kebab-case
- Generates proper frontmatter with tags
- Handles images
- Creates slug mapping report
"""
import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Comprehensive Chinese to English slug mapping
SLUG_DICTIONARY = {
    # Technical terms
    '工程实践': 'engineering-practice',
    '写代码': 'coding',
    '第一步': 'first-step',
    '同学': 'student',
    '为什么': 'why',
    '建议': 'suggest',
    '关注': 'follow',
    '实训营': 'techcamp',
    '工程师': 'engineer',
    '核心竞争力': 'core-competitiveness',
    '优秀': 'excellent',
    '特质': 'qualities',
    '一行之差': 'one-line-difference',
    '文件末尾': 'end-of-file',
    '空行': 'newline',
    '类型系统': 'type-system',
    '编译器': 'compiler',
    '实现': 'implementation',
    '辅助开发': 'assisted-development',
    '新范式': 'new-paradigm',
    '探索': 'explore',
    '未来': 'future',
    '时代': 'era',
    '发展观': 'development-perspective',
    '发布': 'release',
    '全景图': 'roadmap',
    '全民编程': 'programming-for-all',
    '语言': 'language',
    '合并': 'merge',
    '三选一': 'three-options',
    '主分支': 'main-branch',
    '怎么选': 'which-to-choose',
    '才算': 'what-makes',
    '完成': 'complete',
    '应用': 'application',
    '理解': 'understanding',
    '构建': 'building',
    '多模态': 'multimodal',
    '搜索服务': 'search-service',
    '心得': 'insights',
    '代码': 'code',
    '核心': 'core',
    '项目': 'project',
    '产品开发': 'product-development',
    '决策层次': 'decision-layers',
    '快速集成': 'rapid-integration',
    '生态': 'ecosystem',
    '桥梁': 'bridge',
    '绘图': 'drawing',
    '融入': 'integration',
    '产品': 'product',
    '编译': 'compilation',
    '运行时': 'runtime',
    '集成': 'integration',
    '依赖识别': 'dependency-identification',
    '一键交付': 'one-click-delivery',
    '架构设计': 'architecture-design',
    '从何入手': 'where-to-start',
    '认知体会': 'insights',
    '几点': 'several-points',
    '关于': 'about',
    '把小事做好': 'doing-small-things-well',
    '不是什么': 'what-is-not',
    '聊': 'on',
}

# Direct title to English slug mapping
TITLE_TO_SLUG = {
    '工程实践分享 | 把小事做好': 'engineering-practice-doing-small-things-well',
    '工程实践分享｜"写代码"不是第一步！': 'engineering-practice-coding-is-not-first-step',
    '同学，为什么我建议你关注 1024 实训营？': 'why-you-should-join-1024-techcamp',
    '当 AI 能写代码，工程师的核心竞争力是什么？': 'engineer-core-competitiveness-in-ai-era',
    '我眼中的优秀工程师特质': 'qualities-of-excellent-engineers',
    '一行之差：为什么你的文件末尾应该留一个空行？': 'why-end-files-with-newline',
    '从类型系统看XGo编译器的实现': 'understanding-xgo-compiler-through-type-system',
    'AI辅助开发新范式：1024实训营带你探索未来': 'ai-assisted-development-new-paradigm-with-techcamp',
    '许式伟聊AI时代下的工程师发展观': 'xu-shiwei-on-engineer-development-in-ai-era',
    '许式伟发布 XGo 全景图：AI 时代的全民编程语言': 'xu-shiwei-releases-xgo-roadmap-programming-for-all-in-ai-era',
    'GitHub PR 合并三选一：主分支该怎么选？': 'github-pr-merge-strategies-which-to-choose',
    '如何才算"完成"一个AI应用': 'what-makes-ai-application-complete',
    '从类型系统理解 LLGo 编译器的实现': 'understanding-llgo-compiler-through-type-system',
    'Code Review 不是什么——盘点5个常见误区': 'what-code-review-is-not',
    '架构设计从何入手？': 'where-to-start-architecture-design',
    '关于架构设计的几点认知体会': 'insights-on-architecture-design',
    'SPX-Algorithm：构建多模态搜索服务的一些心得': 'spx-algorithm-building-multimodal-search-service',
    '代码不是核心：从 XLink 项目看产品开发的决策层次': 'code-is-not-core-decision-layers-in-xlink-project',
    'llpyg: LLGo 快速集成 Python 生态的桥梁': 'llpyg-bridge-for-llgo-python-integration',
    'X绘图-我们是如何让AI更好的融入我们的产品的': 'xdraw-how-to-integrate-ai-into-products',
    'X绘图：我们如何让 AI 更好地融入产品': 'xdraw-how-to-integrate-ai-into-products',
    'LLGo 中 Python 编译与运行时集成：从依赖识别到一键交付': 'llgo-python-compilation-and-runtime-integration',
    'LLGo 中 Python 编译与运行时集成': 'llgo-python-compilation-and-runtime-integration',
}

# Tag mapping based on keywords
TAG_KEYWORDS = {
    'ai': ['AI', 'ai', '大模型', '智能', '人工智能', 'LLM'],
    'go': ['Go', 'go', 'golang', 'Go+', 'goplus'],
    'compiler': ['编译器', 'XGo', 'LLGo', '类型系统', 'typesystem', 'compiler'],
    'engineering': ['工程实践', '工程师', 'Code Review', 'GitHub', 'PR', '质量', '规范'],
    'architecture': ['架构设计', '架构', '设计', '系统', 'architecture', 'design'],
    'xgo': ['XGo', 'xgo'],
    'llgo': ['LLGo', 'llgo', 'llpyg'],
    'career': ['职业', '发展', '成长', '特质', '核心竞争力', 'career'],
    'python': ['Python', 'python', 'llpyg'],
    'tutorial': ['教程', '指南', '入门', 'guide', 'tutorial'],
    'best-practices': ['最佳实践', '实践', '心得', 'best-practices'],
}


def translate_to_english_slug(title: str) -> str:
    """Translate Chinese title to English kebab-case slug"""
    # Check direct mapping first
    if title in TITLE_TO_SLUG:
        return TITLE_TO_SLUG[title]

    # Build slug using dictionary
    slug_parts = []
    remaining_title = title

    # Try to match phrases from dictionary
    for cn, en in sorted(SLUG_DICTIONARY.items(), key=lambda x: -len(x[0])):
        if cn in remaining_title:
            remaining_title = remaining_title.replace(cn, f'|{en}|')

    # Split and clean
    parts = re.split(r'[|｜\s：:？?！!，,、。]', remaining_title)
    for part in parts:
        if not part.strip():
            continue
        # If already English or alphanumeric, use as-is
        if re.match(r'^[a-zA-Z0-9-]+$', part):
            slug_parts.append(part.lower())

    # Join and clean up
    slug = '-'.join(slug_parts)
    slug = re.sub(r'[^a-z0-9-]', '', slug.lower())
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')

    return slug[:100]  # Limit length


def extract_title_from_content(content: str) -> str:
    """Extract title from markdown content"""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return None


def extract_tags(title: str, content: str, folder_name: str) -> List[str]:
    """Extract relevant tags based on keywords"""
    tags = set()
    text_to_check = (title + ' ' + content + ' ' + folder_name).lower()

    for tag, keywords in TAG_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_to_check:
                tags.add(tag)
                break

    # Always add engineering for general articles if no specific tag
    if not tags:
        tags.add('engineering')

    return sorted(list(tags))


def extract_description(content: str, max_length: int = 150) -> str:
    """Extract first meaningful paragraph as description"""
    # Remove title and empty lines
    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]

    for line in lines:
        if len(line) > 20 and not line.startswith('```') and not line.startswith('*'):
            desc = line[:max_length]
            if len(line) > max_length:
                desc += '...'
            return desc

    return "1024 实训营技术分享文章"


def migrate_article(source_path: Path, index: int, base_date: datetime) -> Dict:
    """Migrate a single article"""
    print(f"\nProcessing: {source_path}")

    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title
    title = extract_title_from_content(content)
    if not title:
        print(f"  ⚠️  No title found, skipping")
        return None

    # Generate metadata
    folder_name = source_path.parent.name
    english_slug = translate_to_english_slug(title)
    tags = extract_tags(title, content, folder_name)
    description = extract_description(content)

    # Generate date (increment by 2 days for each article)
    article_date = base_date + timedelta(days=index * 2)
    date_str = article_date.strftime('%Y-%m-%d')

    # Remove the title from content
    content_lines = content.split('\n')
    if content_lines and content_lines[0].startswith('# '):
        content_lines = content_lines[1:]
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)

    content_body = '\n'.join(content_lines)

    # Handle images
    source_dir = source_path.parent
    for img_pattern in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg']:
        for img_file in source_dir.glob(img_pattern):
            dest_img_dir = Path('website/static/img/blog') / english_slug
            dest_img_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img_file, dest_img_dir / img_file.name)
            # Update image references
            content_body = content_body.replace(f'({img_file.name})', f'(/img/blog/{english_slug}/{img_file.name})')
            content_body = content_body.replace(f'[{img_file.name}]', f'[/img/blog/{english_slug}/{img_file.name}]')

    # Handle images in subdirectories
    for img_dir in source_dir.iterdir():
        if img_dir.is_dir():
            for img_pattern in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg']:
                for img_file in img_dir.glob(img_pattern):
                    dest_img_dir = Path('website/static/img/blog') / english_slug
                    dest_img_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(img_file, dest_img_dir / img_file.name)
                    # Update references
                    content_body = content_body.replace(f'{img_dir.name}/{img_file.name}', f'/img/blog/{english_slug}/{img_file.name}')

    # Create frontmatter
    frontmatter = f"""---
slug: /blog/2025/{english_slug}
title: "{title}"
authors: [techcamp]
tags: [{', '.join(tags)}]
date: {date_str}
description: "{description}"
---

"""

    # Combine
    new_content = frontmatter + content_body

    # Generate filename
    new_filename = f"{date_str}-{english_slug}.md"
    new_path = Path('website/blog') / new_filename

    # Write file
    with open(new_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  ✅ Created: {new_filename}")
    print(f"  📝 Slug: {english_slug}")
    print(f"  🏷️  Tags: {', '.join(tags)}")

    return {
        'source': str(source_path),
        'destination': str(new_path),
        'original_title': title,
        'english_slug': english_slug,
        'date': date_str,
        'tags': tags
    }


def main():
    """Main migration function"""
    print("="*80)
    print("COMPREHENSIVE 2025 ARTICLES MIGRATION")
    print("="*80)

    # Get all markdown files from 2025/
    source_dir = Path('2025')
    source_files = sorted(source_dir.glob('*/*.md'))

    print(f"\nFound {len(source_files)} articles to migrate\n")

    # Base date for articles
    base_date = datetime(2025, 1, 15)

    results = []
    for index, source_file in enumerate(source_files):
        result = migrate_article(source_file, index, base_date)
        if result:
            results.append(result)

    # Print summary
    print("\n" + "="*80)
    print("MIGRATION SUMMARY")
    print("="*80)
    print(f"Total articles migrated: {len(results)}\n")

    # Group by tags
    tags_count = {}
    for result in results:
        for tag in result['tags']:
            tags_count[tag] = tags_count.get(tag, 0) + 1

    print("Tags distribution:")
    for tag, count in sorted(tags_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tag}: {count} articles")

    print("\n" + "="*80)
    print("SLUG TRANSLATION MAPPING")
    print("="*80)
    for result in results:
        print(f"\n  Original: {result['original_title']}")
        print(f"  Slug:     {result['english_slug']}")
        print(f"  Date:     {result['date']}")

    # Save mapping to file
    mapping_file = Path('slug_mapping.json')
    import json
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Slug mapping saved to {mapping_file}")
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Review the migrated files in website/blog/")
    print("2. Test the build: cd website && npm install && npm run build")
    print("3. After verification, delete the 2025/ directory")
    print("="*80)


if __name__ == '__main__':
    main()
