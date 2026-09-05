"""Build the static homepage and its original vector illustration. No dependencies."""
from pathlib import Path
from math import sqrt, sin, pi

ROOT = Path(__file__).resolve().parents[1]
head = (ROOT / 'index.html').read_text(encoding='utf-8').split('<style>')[0].split('<link rel="stylesheet" href="styles/landing.css">')[0]
head = head.replace('content="#07080c"', 'content="#f4f1e8"')
head = head.replace('Abundance: global food, water and electricity comparisons; nominal GDP per person, with no GDP-to-poverty ratio.', 'Abundance: We have more than enough. An open inquiry into resources and access, with an engraved copper planet.')
(ROOT / 'assets').mkdir(exist_ok=True)
lines = []
for y in range(100, 481, 6):
    d = sqrt(max(0, 190**2 - (y-290)**2))
    bend = 18 * sin((y-100)/380*pi)
    lines.append(f'<path d="M {290-d:.2f} {y} Q 290 {y+bend:.2f} {290+d:.2f} {y}"/>')
svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 580 580" fill="none">
<defs><radialGradient id="sun" cx="28%" cy="22%" r="83%"><stop stop-color="#f9cf79"/><stop offset=".52" stop-color="#e67d3e"/><stop offset="1" stop-color="#b34e29"/></radialGradient><pattern id="grain" width="5" height="5" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".65" fill="#552a19" opacity=".25"/></pattern><clipPath id="sphere"><circle cx="290" cy="290" r="190"/></clipPath></defs>
<g stroke="#7c8571" stroke-width=".7" opacity=".35"><circle cx="290" cy="290" r="250"/><path d="M 10 290 H 570 M 290 10 V 570"/><circle cx="290" cy="290" r="230" stroke-dasharray="1 8"/></g>
<ellipse cx="290" cy="305" rx="275" ry="83" transform="rotate(-27 290 305)" stroke="#324b35" stroke-width="1"/>
<circle cx="290" cy="290" r="190" fill="url(#sun)"/>
<g clip-path="url(#sphere)" stroke="#763b27" stroke-width=".85" opacity=".55">''' + ''.join(lines) + '''</g>
<g clip-path="url(#sphere)" stroke="#773f29" opacity=".3"><ellipse cx="290" cy="290" rx="145" ry="190"/><ellipse cx="290" cy="290" rx="80" ry="190"/><path d="M290 100V480"/></g>
<circle cx="290" cy="290" r="190" fill="url(#grain)"/>
<path d="M 49 403 C 65 469 322 411 482 287 C 535 246 548 215 528 192" stroke="#263d2a" stroke-width="1.4"/>
<circle cx="87" cy="420" r="8" fill="#263d2a"/><circle cx="493" cy="160" r="5" fill="#c76433"/>
<g stroke="#263d2a"><path d="M 477 458 h 18 M486 449v18 M 88 130h12 M94 124v12"/></g>
</svg>'''
(ROOT / 'assets/planet.svg').write_text(svg, encoding='utf-8')
body = '''<link rel="stylesheet" href="styles/landing.css">
<script src="scripts/landing.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header wrap">
  <a class="brand" href="./" aria-label="Abundance home"><span class="brand-symbol" aria-hidden="true">✳</span> abundance<span class="brand-period">.</span></a>
  <nav aria-label="Main navigation"><a href="#evidence">The evidence</a><a href="#explore">Explore</a><a class="nav-course" href="course.html">Take the course <span aria-hidden="true">↗</span></a></nav>
</header>
<main id="main">
  <section class="hero wrap" aria-labelledby="hero-title">
    <div class="hero-copy"><p class="eyebrow"><span class="status-dot"></span> An open inquiry into a world of enough</p>
      <h1 id="hero-title">We have<br>more than<br><em>enough.</em></h1>
      <p class="hero-description">So why do so many go without? Explore what humanity produces, what people need, and the distance between the two.</p>
      <div class="hero-actions"><a class="button" href="#evidence">See the arithmetic <span aria-hidden="true">↘</span></a><a class="text-link" href="course.html">Start with the 8-minute course <span aria-hidden="true">↗</span></a></div>
    </div>
    <figure class="hero-art"><div class="art-top"><span>EARTH / OUR SHARED STARTING POINT</span><span>01—01</span></div><img src="assets/planet.svg" width="580" height="580" alt="An engraved copper-colored planet encircled by a single orbit."><figcaption><span>One planet.<br><strong>All of us.</strong></span><span class="art-caption">A question of resources.<br>A question of access.</span></figcaption></figure>
    <div class="hero-bottom"><span>Evidence, with the assumptions left in.</span><a href="#evidence">Scroll to investigate <span aria-hidden="true">↓</span></a></div>
  </section>
  <div class="principles"><div class="wrap"><span>Open data</span><i aria-hidden="true">✳</i><span>Linked sources</span><i aria-hidden="true">✳</i><span>Visible assumptions</span><i aria-hidden="true">✳</i><span>Free to question</span></div></div>
  <section class="evidence wrap" id="evidence" aria-labelledby="evidence-title">
    <div class="section-heading"><p class="eyebrow">01 / The arithmetic</p><div><h2 id="evidence-title">Start with<br><em>what exists.</em></h2><p>A global total divided by people. A useful starting point, with real limits. Choose a resource to look closer.</p></div></div>
    <div class="resource-tabs" role="tablist" aria-label="Explore a resource" hidden>
      <button id="tab-food" role="tab" aria-selected="true" aria-controls="resource-panel" data-resource="food"><span aria-hidden="true">01</span> Food <span aria-hidden="true">↗</span></button>
      <button id="tab-energy" role="tab" aria-selected="false" aria-controls="resource-panel" tabindex="-1" data-resource="energy"><span aria-hidden="true">02</span> Electricity <span aria-hidden="true">↗</span></button>
      <button id="tab-water" role="tab" aria-selected="false" aria-controls="resource-panel" tabindex="-1" data-resource="water"><span aria-hidden="true">03</span> Water <span aria-hidden="true">↗</span></button>
      <button id="tab-output" role="tab" aria-selected="false" aria-controls="resource-panel" tabindex="-1" data-resource="output"><span aria-hidden="true">04</span> Output <span aria-hidden="true">↗</span></button>
    </div>
    <div class="resource-panel" id="resource-panel" role="tabpanel" aria-labelledby="tab-food" tabindex="0">
      <div class="resource-story"><p class="eyebrow" id="resource-kicker">Food / Global dietary energy supply</p><h3 id="resource-title">Enough calories.<br>Unequal access.</h3><p id="resource-description">The global average food supply is above this project’s calorie reference. That does not mean everyone can afford a nutritious diet.</p><a id="resource-source" class="source-link" href="https://www.fao.org/statistics/highlights-archive/highlights-detail/food-balance-sheets-2010-2023/en">FAO Food Balance Sheets · 2023 data ↗</a></div>
      <div class="resource-chart"><div class="resource-number"><span id="resource-ratio">1.43</span><span id="resource-suffix">×</span></div><p id="ratio-caption">global supply / calorie reference</p><div id="comparison"><div class="bar-label"><span id="supply-label">Average food supply</span><strong id="supply-value">3,006 kcal</strong></div><div class="bar-track"><div class="supply-bar"></div></div><div class="bar-label"><span id="reference-label">Project calorie reference</span><strong id="reference-value">2,100 kcal</strong></div><div class="bar-track"><div class="reference-bar" id="reference-bar" style="width:69.86%"></div></div></div><p id="unit-label" class="chart-unit">Per person, per day · linear scale</p></div>
      <div class="resource-note"><span class="note-mark" aria-hidden="true">↳</span><div><strong>What this number doesn’t tell you</strong><p id="resource-caveat">Food supply is not intake. Calorie needs vary with age, body size and activity; the 2,100 kcal figure is a project reference, not a universal requirement. Supply already excludes feed and post-harvest losses.</p><a id="reference-source" href="https://www.fao.org/4/y5686e/y5686e00.htm">Read the reference and its assumptions ↗</a></div></div>
    </div>
    <p class="data-note" id="data-status">Sources use different years. Where needed, calculations use the project’s rounded 2024 population of 8.2 billion. <a href="https://github.com/lordbasilaiassistant-sudo/Abundance/blob/main/methodology.md">Read the methodology ↗</a></p>
    <noscript><p class="data-note">This is the food comparison. <a href="essay.html">Read all resource comparisons in the full essay.</a></p></noscript>
  </section>
  <section class="access-section" aria-labelledby="access-title"><div class="wrap access-layout"><div><p class="eyebrow">02 / The distance between enough and access</p><h2 id="access-title">An average<br>doesn’t feed<br><em>a person.</em></h2></div><div class="access-copy"><span class="access-star" aria-hidden="true">✳</span><p class="large-copy">Resources can exist.<br>People can still go without.</p><p>Geography, infrastructure, conflict, affordability and political choices shape who gets what. Global arithmetic opens the question. It doesn’t settle how we get resources into people’s hands.</p><a class="light-link" href="countries.html">See how it differs by country <span aria-hidden="true">↗</span></a><a class="light-link" href="https://github.com/lordbasilaiassistant-sudo/Abundance/blob/main/papers/counterarguments.md">Read the strongest counterarguments <span aria-hidden="true">↗</span></a></div></div></section>
  <section class="explore wrap" id="explore" aria-labelledby="explore-title"><div class="section-heading"><p class="eyebrow">03 / Follow your curiosity</p><div><h2 id="explore-title">Go beyond<br><em>the headline.</em></h2><p>Learn the argument. Change the assumptions. Look for the places it holds—and the places it breaks.</p></div></div>
    <a class="course-feature" href="course.html"><div><p class="eyebrow">The interactive introduction / About 8 minutes</p><h3>A different way<br>to see <em>enough.</em></h3><p>Seven short lessons. Make a guess, see the numbers,<br class="desktop-break"> and build your own understanding.</p><span class="feature-link">Begin the course <span aria-hidden="true">↗</span></span></div><div class="course-art" aria-hidden="true"><span>÷</span><span>=</span><span>?</span><i>ASK. TEST. RECONSIDER.</i></div></a>
    <div class="reading-list">
      <a href="essay.html"><span class="reading-index">01</span><div><h3>The full argument</h3><p>The arithmetic, the evidence and the honest limits.</p></div><span class="reading-kind">Essay</span><span class="reading-arrow" aria-hidden="true">↗</span></a>
      <a href="countries.html"><span class="reading-index">02</span><div><h3>Beyond the global average</h3><p>Explore country-level data and compare the differences.</p></div><span class="reading-kind">Data explorer</span><span class="reading-arrow" aria-hidden="true">↗</span></a>
      <a href="embed/calculator.html"><span class="reading-index">03</span><div><h3>Run your own numbers</h3><p>Move the redistribution dials. Inspect what changes.</p></div><span class="reading-kind">Calculator</span><span class="reading-arrow" aria-hidden="true">↗</span></a>
      <a href="case-studies.html"><span class="reading-index">04</span><div><h3>What countries have tried</h3><p>Eleven country case studies, including their counter-narratives.</p></div><span class="reading-kind">Case studies</span><span class="reading-arrow" aria-hidden="true">↗</span></a>
      <a href="datacenter-water.html"><span class="reading-index">05</span><div><h3>Waste heat. Drinking water.</h3><p>A design hypothesis, open calculations and a testable next step.</p></div><span class="reading-kind">Design note</span><span class="reading-arrow" aria-hidden="true">↗</span></a>
      <a href="letter.html"><span class="reading-index">06</span><div><h3>To whoever can act</h3><p>An open letter about what we choose to make possible.</p></div><span class="reading-kind">Open letter</span><span class="reading-arrow" aria-hidden="true">↗</span></a>
    </div>
  </section>
  <section class="open-section wrap"><p class="eyebrow">An open project, in every sense.</p><h2>Take the data.<br><em>Question everything.</em></h2><div><p>No paywall. No account. Public-domain work you can read, reuse, challenge and improve.</p><a class="button" href="https://github.com/lordbasilaiassistant-sudo/Abundance">Explore the source <span aria-hidden="true">↗</span></a></div></section>
</main>
<footer class="site-footer wrap"><a class="brand" href="./"><span class="brand-symbol" aria-hidden="true">✳</span> abundance.</a><p>A world of enough is worth investigating.</p><nav aria-label="Footer"><a href="tools/">Free tools ↗</a><a href="https://github.com/lordbasilaiassistant-sudo/Abundance/blob/main/bibliography.md">Bibliography ↗</a><a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 ↗</a></nav></footer>
</body>
</html>
'''
(ROOT / 'index.html').write_text(head + body, encoding='utf-8')
print('Built index.html and assets/planet.svg')
