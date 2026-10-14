"""Build the blog from site.json and Markdown. Run from any directory."""
import html
import json
import re
import shutil
import datetime
from pathlib import Path
from urllib.parse import quote
import markdown

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dist'
config = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
esc = html.escape
posts = []
for file in (ROOT / 'content').glob('*.md'):
    raw = file.read_text(encoding='utf-8-sig')
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', raw, re.S)
    if not match:
        raise ValueError(f'{file.name}: missing article metadata')
    meta = dict(line.split(':', 1) for line in match[1].splitlines() if ':' in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    for key in ('title', 'date', 'category', 'summary'):
        if not meta.get(key):
            raise ValueError(f'{file.name}: missing {key}')
    datetime.date.fromisoformat(meta['date'])
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', file.stem):
        raise ValueError('Use lowercase English letters, numbers and hyphens for filenames')
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc', 'sane_lists'])
    body = md.convert(match[2])
    meta.update(slug=file.stem, body=body, toc=md.toc,
                tags=[t.strip() for t in meta.get('tags', '').split(',') if t.strip()],
                minutes=max(1, round(len(match[2]) / 400)))
    posts.append(meta)
posts.sort(key=lambda p: (p['date'], p['slug']), reverse=True)
OUT.mkdir(exist_ok=True)
for stale in (OUT / 'posts').glob('*.html'):
    stale.unlink()
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)

def shell(title, content, section='articles', depth=0, description=None, base_url=None):
    base = base_url or '../' * depth or './'
    links = [('articles', '文章', 'index.html'), ('archive', '归档', 'archive.html'), ('about', '关于', 'about.html')]
    nav = ''.join(f'<a class="{"active" if section == key else ""}" href="{base}{url}">{label}</a>' for key, label, url in links)
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · {esc(config['title'])}</title><meta name="description" content="{esc(description or config['description'])}">
<meta name="color-scheme" content="light dark"><link rel="icon" href="{base}assets/favicon.svg" type="image/svg+xml">
<script>try{{if(localStorage.getItem('theme')==='dark')document.documentElement.dataset.theme='dark'}}catch(e){{}}</script>
<link rel="stylesheet" href="{base}assets/style.css"><script src="{base}assets/app.js" defer></script></head>
<body><a class="skip" href="#main">跳到正文</a><header><div class="header-inner"><a class="brand" href="{base}index.html"><span class="brand-icon">&gt;_</span>{esc(config['title'])}<span class="brand-sub">/ notes</span></a><nav aria-label="主导航">{nav}<button id="theme" class="theme" aria-label="切换深色模式" title="切换深色模式">◐</button></nav></div></header>
<main id="main">{content}</main><footer><span>© {datetime.date.today().year} {esc(config['author'])} · {esc(config['title'])}</span><span>用文字沉淀思考，用代码探索可能。 <a href="{esc(config['github'])}" target="_blank" rel="noopener">GitHub ↗</a></span></footer></body></html>'''

def write(name, content):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def card(p, i):
    tags = ''.join(f'<span class="tag">{esc(t)}</span>' for t in p['tags'] if t != '示例文章')
    sample = '<span class="sample">示例</span>' if '示例文章' in p['tags'] else ''
    searchable = esc(' '.join([p['title'], p['summary'], p['category'], *p['tags']]), quote=True)
    return f'''<article class="post-card" data-category="{esc(p['category'])}" data-search="{searchable}"><div class="post-meta"><span>{esc(p['category'])}</span><time datetime="{p['date']}">{p['date'].replace('-', '.')}</time><span>{p['minutes']} 分钟阅读</span></div><a class="post-title" href="posts/{p['slug']}.html">{esc(p['title'])}<span class="arrow">↗</span></a><p>{esc(p['summary'])}</p><div class="post-bottom"><div class="tags">{tags}{sample}</div><span class="post-number">/{i:02d}</span></div></article>'''

categories = sorted({p['category'] for p in posts})
filters = '<button class="filter selected" data-filter="all" aria-pressed="true">全部文章</button>' + ''.join(f'<button class="filter" data-filter="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in categories)
hero = '''<section class="hero"><div class="hero-copy"><div class="eyebrow"><span class="status-dot"></span> LEARN · BUILD · SHARE</div><h1>把思考写下来，<br>让代码说话<span class="green">。</span></h1><p>记录代码、思考与每一次小小的进步。<br>这里是我的技术笔记，也是持续学习的轨迹。</p><a class="hero-link" href="#articles">开始阅读 <span>↓</span></a></div><div class="code-window" aria-label="代码装饰"><div class="window-bar"><span class="dots">● ● ●</span><span>hello.cpp</span><span>C++</span></div><div class="code-lines"><div><i>01</i><code><span class="muted">// 每一行代码，都是一个新的开始</span></code></div><div><i>02</i><code><span class="purple">#include</span> <span class="green">&lt;iostream&gt;</span></code></div><div><i>03</i><code>&nbsp;</code></div><div><i>04</i><code><span class="purple">int</span> <span class="blue">main</span>() {{</code></div><div><i>05</i><code>  std::cout &lt;&lt; <span class="green">"Hello, World!"</span>;</code></div><div><i>06</i><code>  <span class="purple">return</span> <span class="orange">0</span>;</code></div><div><i>07</i><code>}}</code></div></div><div class="terminal"><span class="green">❯</span> Hello, World!<span class="cursor"></span></div></div></section>'''
sidebar = f'''<aside class="sidebar"><section class="author-card"><div class="avatar">Q<span>_</span></div><h3>{esc(config['author'])}</h3><div class="author-role">学习 · 实践 · 记录</div><p>欢迎来到我的笔记空间。<br>从一个问题开始，<br>慢慢积累自己的答案。</p><a class="github-link" href="{esc(config['github'])}" target="_blank" rel="noopener">在 GitHub 找到我 ↗</a><div class="stats"><div><strong>{len(posts):02d}</strong><span>篇文章</span></div><div><strong>{len(categories):02d}</strong><span>个分类</span></div></div></section><section class="side-note"><div class="eyebrow">THE LITTLE THINGS</div><p>不必一次理解所有。<br>今天比昨天多懂一点，<br>就已经很好。</p><span>持续学习，保持好奇。</span></section></aside>'''
hero = hero.replace('{{', '{').replace('}}', '}').replace('记录代码、思考与每一次小小的进步。', esc(config['description']))
home = hero + f'''<div class="content-grid" id="articles"><section><div class="section-heading"><div><span class="eyebrow">THE NOTEBOOK</span><h2>最新文章 <span>{len(posts):02d}</span></h2></div><label class="search"><span aria-hidden="true">⌕</span><input id="search" type="search" placeholder="搜索文章…" aria-label="搜索文章"></label></div><div class="filters" aria-label="文章分类">{filters}</div><div id="posts">{''.join(card(p, i) for i, p in enumerate(posts, 1))}</div><p id="empty" hidden>没有找到相关文章，试试其他关键词。</p><div class="end-note">— 暂时写到这里，下一篇正在路上 —</div></section>{sidebar}</div>'''
write('index.html', shell('首页', home))
for index, p in enumerate(posts):
    tags = ''.join(f'<span class="tag">{esc(t)}</span>' for t in p['tags'])
    others = [other for other in posts if other != p]
    related = ''.join(f'<a href="{o["slug"]}.html">{esc(o["title"])} <span>→</span></a>' for o in others[:2])
    article = f'''<div class="article-layout"><article class="article"><a class="back" href="../index.html">← 返回文章列表</a><div class="post-meta"><span>{esc(p['category'])}</span><time datetime="{p['date']}">{p['date']}</time><span>{p['minutes']} 分钟阅读</span></div><h1>{esc(p['title'])}</h1><p class="article-summary">{esc(p['summary'])}</p><div class="tags">{tags}</div><div class="prose">{p['body']}</div><div class="article-end">感谢阅读。把学到的东西写下来，就是下一次进步的起点。</div><section class="related"><h3>继续阅读</h3>{related}</section></article><aside class="toc-box"><div class="eyebrow">ON THIS PAGE</div><h3>文章目录</h3>{p['toc']}<a class="back-top" href="#main">回到顶部 ↑</a></aside></div>'''
    write(f'posts/{p["slug"]}.html', shell(p['title'], article, depth=1, description=p['summary']))
archive = '<section class="page-intro"><div class="eyebrow">THE TIMELINE</div><h1>文章归档<span class="green">。</span></h1><p>按时间整理，回看每一步积累。</p></section><section class="archive-list">'
for year in sorted({p['date'][:4] for p in posts}, reverse=True):
    archive += f'<h2>{year}</h2>'
    for p in posts:
        if p['date'].startswith(year):
            archive += f'<a href="posts/{p["slug"]}.html"><time>{p["date"][5:].replace("-", ".")}</time><span>{esc(p["title"])}</span><small>{esc(p["category"])}</small><b>↗</b></a>'
archive += '</section>'
write('archive.html', shell('归档', archive, 'archive'))
about = f'''<section class="page-intro"><div class="eyebrow">BEHIND THE NOTES</div><h1>关于这里<span class="green">。</span></h1><p>一个用来记录、整理和分享的地方。</p></section><div class="about-grid"><section class="prose about-body"><h2>你好，我是 {esc(config['author'])}。</h2><p>欢迎来到我的个人技术博客。这里用于记录编程学习、整理遇到的问题，也分享项目实践中的思考。</p><h2>这本笔记里有什么</h2><p>从一个小程序到一个完整项目，从报错的排查到概念的理解，每一份笔记都可以成为下一次实践的起点。</p><ul><li>编程与技术学习笔记</li><li>问题排查与解决过程</li><li>项目实践与阶段复盘</li></ul><h2>保持联系</h2><p>你可以在 <a href="{esc(config['github'])}" target="_blank" rel="noopener">GitHub ↗</a> 找到我。</p><blockquote>把复杂的问题拆小，把学到的东西写清楚。</blockquote></section><div class="about-terminal"><span class="eyebrow">PROFILE.JSON</span><pre>{{
  "name": "{esc(config['author'])}",
  "space": "技术札记",
  "mode": "keep learning",
  "next": "one small step"
}}</pre><span class="green">● 持续更新中</span></div></div>'''
write('about.html', shell('关于', about, 'about'))
write('404.html', shell('页面未找到', '<section class="page-intro"><div class="eyebrow">404 / NOT FOUND</div><h1>这页笔记走丢了。</h1><p>可以从首页重新开始。</p><a class="hero-link" href="'+esc(config['url'])+'">返回首页 →</a></section>', base_url=config['url']))
write('.nojekyll', '')
# Build-time checks catch broken internal links before publication.
for page in OUT.rglob('*.html'):
    for target in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding='utf-8')):
        if target.startswith(('https:', 'http:', '#', 'data:')):
            continue
        local = target.split('#')[0]
        if local and not (page.parent / local).resolve().exists():
            raise ValueError(f'Broken link in {page.name}: {target}')
print(f'Built {len(posts)} articles, homepage, archive and about. Internal links verified.')
