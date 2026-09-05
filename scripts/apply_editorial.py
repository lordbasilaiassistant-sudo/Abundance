"""Install the shared reading theme and static navigation; safe to rerun."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
pages = ['essay.html', 'letter.html', 'case-studies.html', 'countries.html', 'datacenter-water.html', 'course.html', 'embed/calculator.html']
for name in pages:
    path = ROOT / name
    text = path.read_text(encoding='utf-8')
    prefix = '../' if name.startswith('embed/') else ''
    css = f'<link rel="stylesheet" href="{prefix}styles/editorial.css">'
    if css not in text:
        text = text.replace('</head>', css + '\n</head>')
    if not prefix and 'class="ab-header"' not in text:
        current = ' aria-current="page"' if name == 'course.html' else ''
        header = f'''<header class="ab-header">
<a class="ab-brand" href="./" aria-label="Abundance home"><span aria-hidden="true">✳</span> abundance.</a>
<nav aria-label="Main navigation"><a href="./#evidence">The evidence</a><a href="./#explore">Explore</a><a href="course.html"{current}>Take the course ↗</a></nav>
</header>'''
        text = text.replace('<body>', '<body>\n' + header, 1)
    path.write_text(text, encoding='utf-8')
    print('Themed', name)
