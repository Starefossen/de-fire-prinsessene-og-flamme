import bs4
import math
import os
import json

# Read original untouched file
with open('source.html', 'r', encoding='utf-8') as f:
    soup = bs4.BeautifulSoup(f, 'html.parser')
    
# Process figure placeholders and inject actual images if they exist
for figure in soup.find_all('figure', attrs={'data-fil': True}):
    img_path = figure['data-fil'] + '.jpg'
    if os.path.exists(img_path):
        figure.clear()
        img = soup.new_tag('img', src=img_path, loading='lazy')
        figure.append(img)
        
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
  /* ---------- BOK-LAYOUT ---------- */
  body {
    overflow-x: hidden;
    overflow-y: auto;
  }
  
  .book-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 1rem;
    scroll-behavior: smooth;
  }
  
  .chapter-content {
    width: 100%;
    max-width: 850px;
    margin: 0 auto 4rem auto;
    
    /* Glassmorphism applied to each chapter */
    background: rgba(29, 35, 70, 0.45);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 28px;
    border: 1px solid rgba(255, 207, 230, 0.08);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    
    padding: 3rem 2rem;
    font-size: 1.15rem;
    line-height: 1.8;
    box-sizing: border-box;
    position: relative;
  }
  
  @media (min-width: 900px) {
    .book-container {
      padding: 4rem 2rem;
    }
    .chapter-content {
      padding: 5rem 6rem;
      font-size: 1.25rem;
      margin-bottom: 6rem;
    }
  }
  
  .chapter-content img, .chapter-content figure {
    max-width: 100%;
    height: auto;
    max-height: 65vh;
    object-fit: contain;
    border-radius: 12px;
    margin: 2rem auto;
    display: block;
    cursor: zoom-in;
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  
  .chapter-content img:hover, .chapter-content figure:hover img {
    transform: scale(1.02);
  }

  /* COVER PAGE OVERRIDES */
  .chapter-content.cover .chapter-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    column-count: auto; /* Disable columns */
  }
  .chapter-content.cover .cover-text {
    margin-bottom: 1.5rem;
  }
  .chapter-content.cover h1 {
    font-size: 2.2rem;
    line-height: 1.1;
    margin-bottom: 0.8rem;
    text-shadow: 0 4px 15px rgba(0,0,0,0.5);
  }
  .chapter-content.cover p {
    font-size: 1rem;
    opacity: 0.9;
    margin-bottom: 0;
  }
  .chapter-content.cover figure {
    margin: 0;
  }
  .chapter-content.cover figure img {
    max-height: 40vh;
  }
  @media (min-width: 900px) {
    .chapter-content.cover .chapter-content {
      flex-direction: row;
      text-align: left;
      justify-content: space-between;
    }
    .chapter-content.cover .cover-text {
      flex: 1;
      padding-right: 3rem;
      margin-bottom: 0;
    }
    .chapter-content.cover h1 {
      font-size: 3.5rem;
      margin-bottom: 1.5rem;
    }
    .chapter-content.cover p {
      font-size: 1.2rem;
    }
    .chapter-content.cover figure {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .chapter-content.cover figure img {
      max-height: 65vh;
    }
  }

  /* TOC PAGE OVERRIDES */
  .chapter-content.toc-page .chapter-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    column-count: auto; /* Disable container columns */
  }
  .chapter-content.toc-page h2 {
    font-size: 2.2rem;
    margin-bottom: 2rem;
    color: var(--rosa);
    text-align: center;
    text-shadow: 0 2px 10px rgba(0,0,0,0.4);
  }
  .chapter-content.toc-page ol {
    width: 100%;
    max-width: 900px;
    column-count: 1;
    column-gap: 2rem;
    list-style: none;
    padding: 0;
    margin: 0;
    counter-reset: toc-counter;
  }
  .chapter-content.toc-page li {
    margin-bottom: 1.2rem;
    break-inside: avoid;
    counter-increment: toc-counter;
  }
  .chapter-content.toc-page a {
    color: #fff;
    text-decoration: none;
    font-size: 1rem;
    font-family: 'Outfit', sans-serif;
    display: flex;
    align-items: center;
    transition: color 0.3s ease, transform 0.3s ease;
    opacity: 0.9;
  }
  .chapter-content.toc-page a:hover {
    color: var(--gull);
    transform: translateX(10px);
    opacity: 1;
  }
  .chapter-content.toc-page a::before {
    content: counter(toc-counter) ".";
    color: var(--rosa);
    font-weight: 700;
    margin-right: 0.8rem;
    font-size: 1rem;
    min-width: 1.2rem;
  }
  @media (min-width: 900px) {
    .chapter-content.toc-page h2 {
      font-size: 3rem;
      margin-bottom: 4rem;
    }
    .chapter-content.toc-page ol {
      column-count: 2;
      column-gap: 5rem;
    }
    .chapter-content.toc-page li {
      margin-bottom: 1.8rem;
    }
    .chapter-content.toc-page a {
      font-size: 1.2rem;
    }
    .chapter-content.toc-page a::before {
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
    main_tag['class'] = main_tag.get('class', []) + ['book-container']
    main_tag['id'] = 'book-container'

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

        # Dynamic CSS Multi-Column Layout! No Python chunking!
        safe_chapter = chapter_title.replace(' ', '-').replace('·', '').replace('—', '-').lower()
        import re
        safe_chapter = re.sub(r'-+', '-', safe_chapter).strip('-')
        
        chap = soup.new_tag('article', attrs={'class': 'chapter-content', 'data-chapter': chapter_title, 'id': f"chapter-{safe_chapter}"})
        
        # Add all elements directly into the chapter container
        for child in list(article.children):
            if isinstance(child, bs4.NavigableString) and child.strip() == '':
                continue
            chap.append(child)
            
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
    overlay.append(soup.new_tag('div', attrs={'class': 'persistent-chapter', 'id': 'persistent-chapter'}))
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
        const container = document.querySelector('.book-container');
        const persistentChapter = document.getElementById('persistent-chapter');
        
        // TOC Links
        document.querySelectorAll('.toc-page a').forEach(a => {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                const targetText = a.textContent.trim();
                const h2s = document.querySelectorAll('.chapter-content h2');
                for (let h2 of h2s) {
                    if (h2.textContent.includes(targetText)) {
                        h2.closest('.chapter-content').scrollIntoView({ behavior: 'smooth' });
                        break;
                    }
                }
            });
        });

                // Keyboard Navigation
        // Removed custom arrow key JS to allow native vertical scrolling

        // Remove horizontal snap JS

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
          const img = e.target.closest('.chapter-content img, .chapter-content figure img');
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
        container.addEventListener('wheel', (e) => {
            // Check if user is scrolling inside a vertically scrollable element
            let target = e.target;
            while(target && target !== container) {
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
cache_name = "prinsessene-v2"
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
