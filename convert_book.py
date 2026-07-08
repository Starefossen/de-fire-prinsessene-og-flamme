import bs4
import math
import os
import json

import subprocess

# Read original untouched file
with open('source.html', 'r', encoding='utf-8') as f:
    soup = bs4.BeautifulSoup(f, 'html.parser')
    
# Process figure placeholders and inject actual images if they exist
for figure in soup.find_all('figure', attrs={'data-fil': True}):
    img_path = figure['data-fil'] + '.jpg'
    if os.path.exists(img_path):
        figure.clear()
        
        # Get image dimensions to prevent WebKit multicol layout bugs
        width, height = None, None
        try:
            out = subprocess.check_output(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', img_path], universal_newlines=True)
            for line in out.split('\n'):
                if 'pixelWidth' in line: width = line.split(':')[1].strip()
                elif 'pixelHeight' in line: height = line.split(':')[1].strip()
        except:
            pass
            
        img = soup.new_tag('img', src=img_path)
        if width and height:
            img['width'] = width
            img['height'] = height
            # Removed lazy loading to fix WebKit multicol bug # Safe to lazy load now that dimensions are known
            
        figure.append(img)
        
# Group portraits and their text into a flexbox wrapper to avoid float bugs in WebKit multicol
for portrait in soup.find_all('figure', class_='portrait'):
    next_p = portrait.find_next_sibling('p')
    if next_p:
        wrapper = soup.new_tag('div', attrs={'class': 'person-wrapper'})
        portrait.wrap(wrapper)
        wrapper.append(next_p)

# Add PWA manifest and fonts to head
head = soup.find('head')
if head:
    # Add manifest
    if not soup.find('link', attrs={'rel': 'manifest'}):
        manifest_link = soup.new_tag('link', rel='manifest', href='manifest.json')
        head.append(manifest_link)
    
    # Add iOS PWA Meta Tags
    if not soup.find('meta', attrs={'name': 'apple-mobile-web-app-capable'}):
        head.append(soup.new_tag('meta', attrs={'name': 'apple-mobile-web-app-capable', 'content': 'yes'}))
        head.append(soup.new_tag('meta', attrs={'name': 'apple-mobile-web-app-status-bar-style', 'content': 'black-translucent'}))
        head.append(soup.new_tag('meta', attrs={'name': 'theme-color', 'content': '#111827'}))
        head.append(soup.new_tag('link', rel='apple-touch-icon', href='bilder/forside.png'))

    # Ensure viewport disables zooming for tactile feel
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        viewport['content'] = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
    else:
        head.append(soup.new_tag('meta', attrs={'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'}))

    # Add Outfit font
    font_link = soup.new_tag('link', rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap')
    head.append(font_link)

# Update CSS
style_tag = soup.find('style')
if style_tag:
    css_additions = """

  /* PERSONGALLERI: constrain group photo height */
  #prolog figure[data-fil="bilder/persongalleri"] img {
    max-height: 30vh !important;
    width: auto;
    margin: 0 auto;
  }
  
  /* ANDRE VENNER: constrain height */
  .illu.andre-venner img {
    max-height: 40vh !important;
    margin-top: 1rem;
  }
  /* OVERVIEW MODE */
  .book-track.overview-mode {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 3rem;
    padding: 6rem 2rem;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    scroll-snap-type: none;
    align-content: flex-start;
    background: rgba(0,0,0,0.5);
  }
  
  .book-track.overview-mode .page {
    flex: 0 0 20vw;
    width: 20vw;
    height: 20vh;
    padding: 0;
    margin: 0;
    position: relative;
    scroll-snap-align: none;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    background: transparent;
  }
  
  .book-track.overview-mode .page:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 40px rgba(255, 207, 230, 0.6);
    z-index: 10;
  }
  
  .book-track.overview-mode .page-content {
    position: absolute;
    top: 0; left: 0;
    width: 100vw !important;
    height: 100vh !important;
    max-width: none !important;
    margin: 0 !important;
    transform: scale(0.2) !important;
    transform-origin: top left;
    pointer-events: none;
    overflow: hidden !important;
  }
  
  @media (max-width: 899px) {
    .book-track.overview-mode .page {
      flex: 0 0 45vw;
      width: 45vw;
      height: 45vh;
    }
    .book-track.overview-mode .page-content {
      transform: scale(0.45) !important;
    }
  }

  .overlay-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    pointer-events: auto;
  }
  
  
  
  .controls-group {
    display: flex;
    gap: 0.6rem;
    align-items: center;
  }

  .action-btn {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    width: 40px;
    height: 40px;
    min-width: 40px;
    box-sizing: border-box;
    padding: 0;
    border-radius: 8px;
    font-size: 1.1rem;
    cursor: pointer;
    backdrop-filter: blur(8px);
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: inherit;
    font-weight: 600;
  }
  .action-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
  .action-btn svg {
    width: 20px;
    height: 20px;
  }
  .overview-btn:hover {
    background: var(--rosa);
    transform: scale(1.05);
  }

  
  p {
    orphans: 3;
    widows: 3;
    margin-bottom: 1.2rem;
  }
  
  h2, h3 {
    break-after: avoid-column;
  }
  figure {
    break-inside: avoid-column;
    page-break-inside: avoid;
    -webkit-column-break-inside: avoid;
    display: inline-block; /* Fixes multicol image vanishing bugs */
    width: 100%;
  }


  
  .page-content p, .page-content h1, .page-content h2, .page-content h3, .page-content h4, .page-content li {
    font-size: calc(1em * var(--font-scale, 1));
  }

  
  .person-wrapper {
    display: inline-flex;
    width: 100%;
    flex-direction: row;
    gap: 1.5rem;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  
  .portrait {
    flex: 0 0 140px;
    min-width: 140px; /* Force minimum width to prevent WebKit flex collapse */
    margin: 0 !important;
    border-radius: 20px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    background: #111827; /* Placeholder background */
    aspect-ratio: 1/1;
    overflow: hidden;
  }
  .portrait img {
    height: 100%;
    width: 100%;
    object-fit: cover;
  }

  /* ---------- BOK-LAYOUT (Scroll Snapping) ---------- */
  body {
    overflow: hidden;
    position: relative;
    letter-spacing: 0.02em;
    overflow-wrap: break-word;
    word-wrap: break-word;
    -webkit-hyphens: auto;
    hyphens: auto;
  }
  p {
    margin-bottom: 1.2em;
  }
  .book-track {
    display: flex;
    overflow-x: auto;
    overflow-y: hidden;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    height: 100svh;
    width: 100vw;
    scrollbar-width: none;
    -ms-overflow-style: none;
  }
  .book-track::-webkit-scrollbar {
    display: none;
  }
  
  .page {
    flex: 0 0 100vw;
    height: 100svh;
    scroll-snap-align: start;
    scroll-snap-stop: always;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    position: relative;
    box-sizing: border-box;
  }

  /* Universal Spread Layout for Chapters */
  .page-content {
    display: block;
    width: 100%;
    max-width: 1400px;
    height: calc(100svh - 4rem);
    margin: 0 auto;
    
    /* Glassmorphism book spread */
    background: rgba(29, 35, 70, 0.45);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 28px;
    border: 1px solid rgba(255, 207, 230, 0.08);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    
    padding: 1.5rem 1.2rem;
    box-sizing: border-box;
    
    /* Flow */
    column-count: auto; /* Disable columns on mobile to allow vertical scroll */
    column-fill: balance;
    column-gap: 3rem;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: none;
  }
  
  .chapter {
    display: contents;
  }

  @media (max-width: 899px) {
    .chapter {
      display: block;
      flex: 0 0 100vw;
      height: 100svh;
      overflow-y: auto;
      overflow-x: hidden;
      scroll-snap-align: start;
      scroll-snap-stop: always;
      padding: 4rem 0; /* Space for persistent headers */
      box-sizing: border-box;
    }
    .page {
      flex: none;
      height: auto;
      width: 100vw;
      scroll-snap-align: none;
      padding: 1rem 1.5rem;
    }
    .page-content {
      height: auto;
      overflow-y: visible;
      padding: 2rem 1.5rem;
      column-count: 1;
      column-gap: 0;
    }
    .nav-zone {
      display: none !important;
    }
  }

  .page-content::-webkit-scrollbar { display: none; }

  @media (min-width: 900px) {
    .page-content {
      padding: 3rem 4rem;
      column-count: 2;
      column-gap: 6rem;
    }
  }

  .page-content > * {
    margin-bottom: 1.5rem;
  }
  
  /* IMAGE STYLING — cosmetic only, no display override */
  .page-content img {
    max-width: 100%;
    height: auto;
    max-height: 40vh;
    object-fit: contain;
    border-radius: 12px;
    display: block;
    margin-left: auto;
    margin-right: auto;
    cursor: zoom-in;
  }
  
  .page-content .illu img {
    aspect-ratio: 4 / 3;
    object-fit: cover;
  }
  
  .page-content .illu.forside img {
    aspect-ratio: auto;
    object-fit: contain;
  }
  /* FIGURE STYLING — MUST stay inline-block to prevent WebKit multicol vanishing */
  .page-content figure {
    max-width: 100%;
    margin-bottom: 1.2rem;
    cursor: zoom-in;
  }
  
  /* COVER PAGE IMAGE FIX */
  .page.cover figure.forside {
    width: 100% !important;
    max-width: 100%;
    margin: 0 !important;
  }
  .page.cover figure.forside img {
    width: 100%;
    max-height: calc(100svh - 14rem) !important;
    object-fit: contain;
    margin: 0;
  }
  /* COVER PAGE OVERRIDES (STABLE FLEXBOX) */
  .page.cover .page-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    column-count: auto; /* Disable columns */
  }
  .page.cover .cover-text {
    flex: 1;
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  @media (min-width: 900px) {
    .page.cover .page-content {
      flex-direction: row;
      text-align: left;
      justify-content: space-between;
      gap: 4rem;
    }
    .page.cover .cover-text {
      flex: 1;
      margin-bottom: 0;
    }
    .page.cover figure.forside {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .page.cover figure.forside img {
      max-height: 65vh !important;
    }
  }
  /* COVER PAGE TYPOGRAPHY */
  .page.cover .cover-text {
    margin-bottom: 1.5rem;
  }
  .page.cover h1 {
    font-size: 2.2rem;
    line-height: 1.1;
    margin-bottom: 0.8rem;
    text-shadow: 0 4px 15px rgba(0,0,0,0.5);
  }
  .page.cover p {
    font-size: 1rem;
    opacity: 0.9;
    margin-bottom: 0;
  }
  .page.cover p.under {
    margin-bottom: 1.5rem;
  }
  .page.cover figure {
    margin: 0;
  }
  .page.cover figure img {
    max-height: 40vh;
    max-width: 100%;
    object-fit: contain;
  }
  .page.cover .slott {
    margin-top: 2rem;
    width: 100%;
    max-height: 15vh;
    opacity: 0.7;
  }
  @media (min-width: 900px) {
    .page.cover h1 {
      font-size: 3.5rem;
      margin-bottom: 1.5rem;
    }
    .page.cover p {
      font-size: 1.2rem;
    }
    .page.cover figure img {
      max-height: 65vh;
    }
  }

  /* TOC PAGE OVERRIDES */
  .page.toc-page .page-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    column-count: auto; /* Disable container columns */
  }
  .page.toc-page h2 {
    font-size: 2.2rem;
    margin-bottom: 2rem;
    color: var(--rosa);
    text-align: center;
    text-shadow: 0 2px 10px rgba(0,0,0,0.4);
  }
  .page.toc-page ol {
    width: 100%;
    max-width: 900px;
    column-count: 1;
    column-gap: 2rem;
    list-style: none;
    padding: 0;
    margin: 0;
    counter-reset: toc-counter;
  }
  .page.toc-page li {
    margin-bottom: 1.2rem;
    break-inside: avoid;
    counter-increment: toc-counter;
  }
  .page.toc-page a {
    color: #fff;
    text-decoration: none;
    font-size: 1rem;
    font-family: 'Outfit', sans-serif;
    display: flex;
    align-items: center;
    transition: color 0.3s ease, transform 0.3s ease;
    opacity: 0.9;
  }
  .page.toc-page a:hover {
    color: var(--gull);
    transform: translateX(10px);
    opacity: 1;
  }
  .page.toc-page a::before {
    content: counter(toc-counter) ".";
    color: var(--rosa);
    font-weight: 700;
    margin-right: 0.8rem;
    font-size: 1rem;
    min-width: 1.2rem;
  }
  @media (min-width: 900px) {
    .page.toc-page h2 {
      font-size: 3rem;
      margin-bottom: 4rem;
    }
    .page.toc-page ol {
      column-count: 2;
      column-gap: 5rem;
    }
    .page.toc-page li {
      margin-bottom: 1.8rem;
    }
    .page.toc-page a {
      font-size: 1.2rem;
    }
    .page.toc-page a::before {
      font-size: 1.2rem;
      margin-right: 1.5rem;
      min-width: 1.5rem;
    }
  }

  /* Navigation zones */
  .nav-zone {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 8vw;
    z-index: 50;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease, background 0.3s ease;
    color: rgba(255, 255, 255, 0.6);
    font-size: 3rem;
  }
  .nav-zone.left { 
    left: 0; 
  }
  .nav-zone.left:hover {
    opacity: 1;
    background: linear-gradient(to right, rgba(0,0,0,0.3), transparent);
  }
  .nav-zone.right { 
    right: 0; 
  }
  .nav-zone.right:hover {
    opacity: 1;
    background: linear-gradient(to left, rgba(0,0,0,0.3), transparent);
  }
  
  @media (max-width: 899px) {
    /* Hide nav zones on mobile to prevent accidental jumping when scrolling */
    .nav-zone {
      display: none !important;
    }
  }
  
  .read-again-btn {
    margin-top: 3rem;
    padding: 1rem 2.5rem;
    background: rgba(255, 207, 230, 0.2);
    border: 1px solid var(--rosa);
    color: white;
    font-family: 'Outfit', sans-serif;
    font-size: 1.2rem;
    text-decoration: none;
    border-radius: 50px;
    transition: all 0.3s ease;
    display: inline-block;
  }
  .read-again-btn:hover {
    background: var(--rosa);
    box-shadow: 0 0 15px var(--rosa);
    transform: scale(1.05);
  }
  
  /* Lightbox Animation */
  .lightbox {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(22, 27, 56, 0.9);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
    cursor: zoom-out;
  }
  .lightbox.active {
    opacity: 1;
    pointer-events: all;
  }
  .lightbox img {
    max-width: 95vw;
    max-height: 95vh;
    border-radius: 16px;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    transform: scale(0.9);
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .lightbox.active img {
    transform: scale(1);
  }
  
  /* Persistent Overlay Header/Footer */
  .book-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 100;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1.5rem 2rem;
  }
  
  .persistent-chapter {
    font-family: 'Outfit', sans-serif;
    font-size: 0.9rem;
    color: var(--gull);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    text-align: center;
    opacity: 0;
    transition: opacity 0.4s ease;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
  }
  
  .persistent-page {
    font-family: 'Outfit', sans-serif;
    font-size: 0.9rem;
    color: var(--lavendel);
    letter-spacing: 0.1em;
    text-align: center;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    transition: opacity 0.4s ease;
  }

  /* Hide original up links */
  .opp { display: none !important; }
"""
    style_tag.append(css_additions)

main_tag = soup.find('main')
if main_tag:
    main_tag['class'] = main_tag.get('class', []) + ['book-track']
    main_tag['id'] = 'book-track'

    new_children = []

    # Process Cover
    header = soup.find('header', class_='omslag')
    if header:
        chap = soup.new_tag('article', attrs={'class': 'chapter'})
        page = soup.new_tag('section', attrs={'class': 'page cover'})
        content = soup.new_tag('div', attrs={'class': 'page-content'})
        
        text_wrapper = soup.new_tag('div', attrs={'class': 'cover-text'})
        for child in list(header.children):
            if child.name == 'figure':
                content.append(child)
            else:
                text_wrapper.append(child)
                
        content.insert(0, text_wrapper)
        page.append(content)
        chap.append(page)
        new_children.append(chap)
        header.extract()

    # Process TOC
    nav = soup.find('nav', class_='toc')
    if nav:
        chap = soup.new_tag('article', attrs={'class': 'chapter'})
        page = soup.new_tag('section', attrs={'class': 'page toc-page'})
        content = soup.new_tag('div', attrs={'class': 'page-content'})
        for child in list(nav.children):
            content.append(child)
        page.append(content)
        chap.append(page)
        new_children.append(chap)
        nav.extract()

    # Process chapters
    articles = soup.find_all('article', class_='kap')
    for article in articles:
        kap_nr = article.find('p', class_='kap-nr')
        h2 = article.find('h2')
        chapter_title = ""
        if kap_nr and h2:
            chapter_title = f"{kap_nr.text.strip().replace(' · ', ' — ')} — {h2.text.strip()}"
        elif h2:
            chapter_title = h2.text.strip()

        # Extract elements and chunk based on manual <hr class="pb"> tags
        all_elements = []
        for child in list(article.children):
            if isinstance(child, bs4.NavigableString) and child.strip() == '':
                continue
            all_elements.append(child)
            
        chunks = []
        current_chunk = []
        
        for el in all_elements:
            if el.name == 'hr' and 'pb' in el.get('class', []):
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = []
                continue
            current_chunk.append(el)
            
        if current_chunk:
            chunks.append(current_chunk)
            
        chap = soup.new_tag('article', attrs={'class': 'chapter'})
        for i in range(len(chunks)):
            # Give each page an ID to allow deep linking
            safe_chapter = chapter_title.replace(' ', '-').replace('·', '').replace('—', '-').lower()
            import re
            safe_chapter = re.sub(r'-+', '-', safe_chapter).strip('-')
            page_id = f"page-{safe_chapter}-{i+1}"
            
            page = soup.new_tag('section', attrs={'class': 'page', 'data-chapter': chapter_title, 'id': page_id})
            content = soup.new_tag('div', attrs={'class': 'page-content'})
            
            chunk = chunks[i]
            for el in chunk:
                content.append(el)
            
            page.append(content)
            chap.append(page)
            
        new_children.append(chap)
            
        article.extract()

    # Process footer
    footer = soup.find('footer')
    if footer:
        chap = soup.new_tag('article', attrs={'class': 'chapter'})
        page = soup.new_tag('section', attrs={'class': 'page'})
        content = soup.new_tag('div', attrs={'class': 'page-content', 'style': 'display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;'})
        
        for child in list(footer.children):
            content.append(child)
            
        btn = soup.new_tag('a', attrs={'href': '#', 'class': 'read-again-btn'})
        btn.string = "Les boken igjen"
        content.append(btn)
        
        page.append(content)
        chap.append(page)
        new_children.append(chap)
        footer.extract()

    # Append all pages to main
    for child in new_children:
        main_tag.append(child)

# Add Navigation Zones and Overlay
body = soup.find('body')
if body:
    overlay = soup.new_tag('div', attrs={'class': 'book-overlay'})
    
    header_row = soup.new_tag('div', attrs={'class': 'overlay-header'})
    header_row.append(soup.new_tag('div', attrs={'class': 'persistent-chapter', 'id': 'persistent-chapter'}))
    
    
    # Group the controls
    controls_group = soup.new_tag('div', attrs={'class': 'controls-group'})
    
    # Font size down
    font_down_btn = soup.new_tag('button', attrs={'id': 'font-down-btn', 'class': 'action-btn'})
    font_down_btn.string = "A-"
    controls_group.append(font_down_btn)
    
    # Font size up
    font_up_btn = soup.new_tag('button', attrs={'id': 'font-up-btn', 'class': 'action-btn'})
    font_up_btn.string = "A+"
    controls_group.append(font_up_btn)

    # Overview button (SVG icon)
    overview_btn = soup.new_tag('button', attrs={'id': 'overview-btn', 'class': 'action-btn'})
    overview_btn.append(bs4.BeautifulSoup('<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>', 'html.parser'))
    controls_group.append(overview_btn)
    
    header_row.append(controls_group)

    
    overlay.append(header_row)
    overlay.append(soup.new_tag('div', attrs={'class': 'persistent-page', 'id': 'persistent-page'}))
    body.insert(0, overlay)

    script = soup.new_tag('script')
    script.string = """
      document.addEventListener('DOMContentLoaded', () => {
        // Register Service Worker for Offline PWA
        if ('serviceWorker' in navigator) {
          window.addEventListener('load', () => {
            navigator.serviceWorker.register('sw.js').catch(err => console.log('SW registration failed:', err));
          });
        }
        
        const pages = document.querySelectorAll('.page');
        const bookTrack = document.getElementById('book-track');
        const persistentChapter = document.getElementById('persistent-chapter');
        const persistentPage = document.getElementById('persistent-page');
        const overviewBtn = document.getElementById('overview-btn');
        overviewBtn.addEventListener('click', () => {
            bookTrack.classList.toggle('overview-mode');
            if (bookTrack.classList.contains('overview-mode')) {
                overviewBtn.innerHTML = '<svg fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
            } else {
                overviewBtn.innerHTML = '<svg fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24"><rect height="7" rx="1" width="7" x="3" y="3"></rect><rect height="7" rx="1" width="7" x="14" y="3"></rect><rect height="7" rx="1" width="7" x="14" y="14"></rect><rect height="7" rx="1" width="7" x="3" y="14"></rect></svg>';
                // Find currently visible page and scroll to it
                const current = Array.from(pages).find(p => p.getBoundingClientRect().left >= -10 && p.getBoundingClientRect().left < window.innerWidth - 10);
                if (current) current.scrollIntoView({ behavior: 'auto' });
            }
        });
        
        pages.forEach(page => {
            page.addEventListener('click', (e) => {
                if (bookTrack.classList.contains('overview-mode')) {
                    bookTrack.classList.remove('overview-mode');
                    overviewBtn.innerHTML = '<svg fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24"><rect height="7" rx="1" width="7" x="3" y="3"></rect><rect height="7" rx="1" width="7" x="14" y="3"></rect><rect height="7" rx="1" width="7" x="14" y="14"></rect><rect height="7" rx="1" width="7" x="3" y="14"></rect></svg>';
                    page.scrollIntoView({ behavior: 'auto' });
                }
            });
        });

        
        pages.forEach((page, index) => {
          if (index > 0) {
            const leftZone = document.createElement('div');
            leftZone.className = 'nav-zone left';
            leftZone.innerHTML = '&#10094;';
            leftZone.addEventListener('click', () => {
              pages[index - 1].scrollIntoView({ behavior: 'smooth' });
            });
            page.appendChild(leftZone);
          }

          if (index < pages.length - 1) {
            const rightZone = document.createElement('div');
            rightZone.className = 'nav-zone right';
            rightZone.innerHTML = '&#10095;';
            rightZone.addEventListener('click', () => {
              pages[index + 1].scrollIntoView({ behavior: 'smooth' });
            });
            page.appendChild(rightZone);
          }
        });
        
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
              if (entry.target.id) {
                history.replaceState(null, null, '#' + entry.target.id);
              }
              const index = Array.from(pages).indexOf(entry.target);
              persistentPage.textContent = `Side ${index + 1} av ${pages.length}`;
              
              const chapterTitle = entry.target.getAttribute('data-chapter');
              if (chapterTitle) {
                persistentChapter.textContent = chapterTitle;
                persistentChapter.style.opacity = '1';
              } else {
                persistentChapter.style.opacity = '0';
              }
            }
          });
        }, {
          threshold: 0.5
        });

        pages.forEach(page => observer.observe(page));
        
        document.querySelectorAll('.toc-page a').forEach(a => {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                const targetText = a.textContent.trim();
                const h2s = document.querySelectorAll('.page h2');
                for (let h2 of h2s) {
                    if (h2.textContent.includes(targetText)) {
                        h2.closest('.page').scrollIntoView({ behavior: 'smooth' });
                        break;
                    }
                }
            });
        });

        // Keyboard Navigation (Arrow keys)
        let isScrolling = false;
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
                e.preventDefault(); // Stop native browser scroll
                if (isScrolling) return;
                
                if (bookTrack.classList.contains('overview-mode')) return;
                
                const current = Array.from(pages).findIndex(p => p.getBoundingClientRect().left >= -10 && p.getBoundingClientRect().left < window.innerWidth - 10);
                if (e.key === 'ArrowRight' && current >= 0 && current < pages.length - 1) {
                    isScrolling = true;
                    pages[current + 1].scrollIntoView({ behavior: 'smooth' });
                    setTimeout(() => isScrolling = false, 600);
                } else if (e.key === 'ArrowLeft' && current > 0) {
                    isScrolling = true;
                    pages[current - 1].scrollIntoView({ behavior: 'smooth' });
                    setTimeout(() => isScrolling = false, 600);
                }
            }
        });
        
        // Handle deep link on load
        if (window.location.hash) {
            try {
                const targetPage = document.getElementById(window.location.hash.substring(1));
                if (targetPage) {
                    setTimeout(() => targetPage.scrollIntoView(), 100);
                }
            } catch (e) {
                console.error('Invalid hash:', e);
            }
        }
        
        // Lightbox Animation Logic
        const lightbox = document.createElement('div');
        lightbox.className = 'lightbox';
        const lbImg = document.createElement('img');
        lightbox.appendChild(lbImg);
        document.body.appendChild(lightbox);

        document.body.addEventListener('click', (e) => {
          const img = e.target.closest('.page-content img, .page-content figure img');
          if (img) {
            e.preventDefault();
            e.stopPropagation();
            lbImg.src = img.src;
            lightbox.classList.add('active');
          }
        });

        lightbox.addEventListener('click', () => {
          lightbox.classList.remove('active');
        });
        
        // Read Again Button
        const readAgainBtn = document.querySelector('.read-again-btn');
        if (readAgainBtn) {
            readAgainBtn.addEventListener('click', (e) => {
                e.preventDefault();
                pages[0].scrollIntoView({ behavior: 'smooth' });
            });
        }
        
        // Mouse Wheel to Horizontal Scroll Translation
        let wheelTimeout;
        
        let fontScale = 1;
        document.getElementById('font-up-btn')?.addEventListener('click', () => {
            fontScale += 0.1;
            document.documentElement.style.setProperty('--font-scale', fontScale);
        });
        document.getElementById('font-down-btn')?.addEventListener('click', () => {
            fontScale = Math.max(0.5, fontScale - 0.1);
            document.documentElement.style.setProperty('--font-scale', fontScale);
        });

        bookTrack.addEventListener('wheel', (e) => {
            if (bookTrack.classList.contains('overview-mode')) return;
            // Check if user is scrolling inside a vertically scrollable element
            let target = e.target;
            while(target && target !== bookTrack) {
                if (target.scrollHeight > target.clientHeight) return;
                target = target.parentNode;
            }
            
            if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
                e.preventDefault();
                if (wheelTimeout) return;
                
                const current = Array.from(pages).findIndex(p => p.getBoundingClientRect().left >= -10 && p.getBoundingClientRect().left < window.innerWidth - 10);
                if (e.deltaY > 20 && current >= 0 && current < pages.length - 1) {
                    pages[current + 1].scrollIntoView({ behavior: 'smooth' });
                    wheelTimeout = setTimeout(() => wheelTimeout = null, 600);
                } else if (e.deltaY < -20 && current > 0) {
                    pages[current - 1].scrollIntoView({ behavior: 'smooth' });
                    wheelTimeout = setTimeout(() => wheelTimeout = null, 600);
                }
            }
        }, { passive: false });
      });
    """
    body.append(script)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

# Generate PWA Manifest
manifest = {
    "name": "De fire prinsessene og Flamme",
    "short_name": "Prinsessene",
    "start_url": "./index.html",
    "display": "standalone",
    "background_color": "#111827",
    "theme_color": "#ffcfe6",
    "icons": [
        {
            "src": "bilder/forside.jpg",
            "sizes": "1024x1024",
            "type": "image/jpeg",
            "purpose": "any maskable"
        }
    ]
}
with open('manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

# Generate Service Worker
import time
cache_name = f"prinsessene-v{int(time.time())}"
assets = ["./", "./index.html", "./manifest.json"]

if os.path.exists("bilder"):
    for file in os.listdir("bilder"):
        if file.endswith(".jpg"):
            assets.append(f"./bilder/{file}")

sw_content = f"""const CACHE_NAME = '{cache_name}';
const ASSETS = {json.dumps(assets, separators=(',', ':'))};

self.addEventListener('install', event => {{
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
}});

self.addEventListener('activate', event => {{
  event.waitUntil(
    caches.keys().then(keys => {{
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    }}).then(() => self.clients.claim())
  );
}});

self.addEventListener('fetch', event => {{
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
}});
"""
with open('sw.js', 'w', encoding='utf-8') as f:
    f.write(sw_content)
