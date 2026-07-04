#!/usr/bin/env python3
"""Build static HTML blog pages from markdown files (no external dependencies)."""

import os
import re
from pathlib import Path
from datetime import datetime


def simple_markdown_to_html(content):
    """Convert markdown to HTML using basic regex (no external libs)."""
    # Remove frontmatter
    content = re.sub(r'^---\n[\s\S]+?\n---\n', '', content)

    # Headers: # → <h1>, ## → <h2>, etc.
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)

    # Bold: **text** → <strong>text</strong>
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)

    # Italic: *text* → <em>text</em>
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)

    # Links: [text](url) → <a href="url">text</a>
    content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', content)

    # Horizontal rule: --- → <hr>
    content = re.sub(r'^---$', '<hr>', content, flags=re.MULTILINE)

    # Paragraphs: double newline → </p><p>
    paragraphs = re.split(r'\n\n+', content.strip())
    html_paragraphs = []
    for para in paragraphs:
        if para.strip().startswith('<'):
            html_paragraphs.append(para)
        elif para.strip():
            html_paragraphs.append(f'<p>{para.strip()}</p>')

    return '\n'.join(html_paragraphs)


def extract_frontmatter(content):
    """Extract metadata from markdown frontmatter."""
    match = re.match(r'^---\n([\s\S]+?)\n---', content)
    if match:
        frontmatter_text = match.group(1)
        frontmatter = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter, content[match.end():].strip()
    return {}, content


def extract_title(content):
    """Extract H1 title from markdown."""
    match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    return match.group(1) if match else 'Untitled'


def extract_excerpt(content, length=160):
    """Extract excerpt from markdown."""
    content = re.sub(r'^---\n[\s\S]+?\n---\n', '', content)
    content = re.sub(r'^#{1,6}\s+.+$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', content)
    content = re.sub(r'[*_`~]', '', content)
    content = ' '.join(content.split())

    if len(content) > length:
        return content[:length] + '...'
    return content


def escape_html(text):
    """Escape HTML special characters."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def generate_post_page(slug, title, content, date=''):
    """Generate HTML page for a single blog post."""
    content_html = simple_markdown_to_html(content)
    excerpt = escape_html(extract_excerpt(content, 155))
    title_escaped = escape_html(title)

    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped} — Mosaic Hostel Varanasi Blog</title>
    <meta name="description" content="{excerpt}">
    <link rel="canonical" href="https://www.mosaichostels.com/blog/{slug}">
    <meta property="og:title" content="{title_escaped}">
    <meta property="og:description" content="{excerpt}">
    <meta property="og:image" content="https://www.mosaichostels.com/images/IMG_1928.JPG">
    <meta property="og:type" content="article">
    <link rel="stylesheet" href="/styles/global.css">
    <style>
        .blog-post {{ max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.8; }}
        .blog-post h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .blog-post h2 {{ font-size: 24px; margin-top: 30px; margin-bottom: 15px; }}
        .blog-post h3 {{ font-size: 20px; margin-top: 20px; margin-bottom: 12px; }}
        .blog-post p {{ margin-bottom: 15px; }}
        .blog-post a {{ color: #3498db; text-decoration: none; }}
        .blog-post a:hover {{ text-decoration: underline; }}
        .blog-nav {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1; }}
        .blog-nav a {{ display: inline-block; padding: 10px 20px; background: #3498db; color: white; border-radius: 5px; margin-right: 10px; margin-bottom: 10px; }}
    </style>
    <script type="application/ld+json">
    {{"@context":"https://schema.org","@type":"BlogPosting","headline":"{title_escaped}","description":"{excerpt}","image":"https://www.mosaichostels.com/images/IMG_1928.JPG","datePublished":"{date or datetime.now().strftime('%Y-%m-%d')}","author":{{"@type":"Organization","name":"Mosaic Hostel Varanasi"}}}}
    </script>
</head>
<body>
    <div id="navbar-container"></div>
    <h1 style="position:absolute;left:-9999px;">{title_escaped}</h1>
    <div class="blog-post">
        {content_html}
        <div class="blog-nav">
            <a href="/blog">← Back to Blog</a>
            <a href="/">← Home</a>
        </div>
    </div>
    <script src="/components/navbar.js"></script>
</body>
</html>"""

    return page_html


def generate_blog_listing(posts):
    """Generate blog listing page."""
    posts_html = ''
    for post in posts:
        posts_html += f"""    <div class="blog-card">
        <h3><a href="/blog/{post['slug']}">{escape_html(post['title'])}</a></h3>
        <p class="blog-date">{post.get('date', 'Undated')}</p>
        <p>{escape_html(post['excerpt'])}</p>
        <a href="/blog/{post['slug']}" class="read-more">Read More →</a>
    </div>
"""

    listing_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Guides — Mosaic Hostel Varanasi Blog</title>
    <meta name="description" content="Travel guides, tips, and stories from Varanasi. Learn about Assi Ghat, solo female travel, hostels, and local experiences.">
    <link rel="canonical" href="https://www.mosaichostels.com/blog">
    <meta property="og:image" content="https://www.mosaichostels.com/images/IMG_1928.JPG">
    <link rel="stylesheet" href="/styles/global.css">
    <style>
        .blog-container {{ max-width: 900px; margin: 40px auto; padding: 20px; }}
        .blog-card {{ background: white; border: 1px solid #ecf0f1; border-radius: 8px; padding: 25px; margin-bottom: 25px; }}
        .blog-card h3 {{ margin-top: 0; margin-bottom: 10px; }}
        .blog-card a {{ color: #3498db; text-decoration: none; }}
        .blog-card a:hover {{ text-decoration: underline; }}
        .blog-date {{ color: #7f8c8d; font-size: 14px; margin-bottom: 10px; }}
        .blog-card p {{ margin-bottom: 15px; }}
        .read-more {{ display: inline-block; color: #3498db; font-weight: bold; }}
    </style>
</head>
<body>
    <div id="navbar-container"></div>
    <h1 style="position:absolute;left:-9999px;">Travel Guides — Varanasi Blog</h1>
    <div class="blog-container">
        <h2>Travel Guides & Stories</h2>
        <p>Expert guides to Varanasi, Assi Ghat, solo travel, and hostel tips from our team.</p>
{posts_html}
    </div>
    <script src="/components/navbar.js"></script>
</body>
</html>"""

    return listing_html


def main():
    """Build blog pages from markdown files."""
    blogs_dir = Path('blogs')
    blog_output_dir = Path('blog')

    if not blogs_dir.exists():
        print(f"ERROR: {blogs_dir} directory not found")
        return

    blog_output_dir.mkdir(exist_ok=True)

    posts = []
    markdown_files = sorted(blogs_dir.glob('*.md'))

    print(f"Building {len(markdown_files)} blog posts...")

    for md_file in markdown_files:
        slug = md_file.stem

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter, body = extract_frontmatter(content)
        title = extract_title(body)
        date = frontmatter.get('date', '')
        excerpt = extract_excerpt(body)

        post_html = generate_post_page(slug, title, content, date)

        post_dir = blog_output_dir / slug
        post_dir.mkdir(exist_ok=True)

        with open(post_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(post_html)

        print(f"  ✓ {slug}")

        posts.append({
            'slug': slug,
            'title': title,
            'excerpt': excerpt,
            'date': date
        })

    listing_html = generate_blog_listing(posts)
    with open(blog_output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(listing_html)

    print(f"\n✅ Blog build complete: {len(posts)} posts as static HTML")


if __name__ == '__main__':
    main()
