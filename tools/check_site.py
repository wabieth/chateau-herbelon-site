#!/usr/bin/env python3
"""Vérifie le site après chaque modification : SEO/GEO, contenu, langues, affichage.

    python3 tools/check_site.py            # tout (lance un serveur local et un navigateur)
    python3 tools/check_site.py --static   # sans navigateur (balises, textes, fichiers)

Sort en erreur (code 1) s'il trouve un problème bloquant ; les avertissements sont listés sans bloquer.
À lancer APRÈS `python3 tools/build_pages.py`.
"""
import json, re, sys, pathlib, html, subprocess, time, socket

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_pages as B  # noqa: E402

errors, warnings = [], []
def err(page, msg): errors.append("%s : %s" % (page or "site", msg))
def warn(page, msg): warnings.append("%s : %s" % (page or "site", msg))

# Mots à ne jamais publier (décisions prises avec Étienne)
BANNED = {
    "Mouret": "nom du chef non confirmé : écrire « notre chef »",
    "coworking": "le coworking n’est plus proposé",
    "Castillan": "ancien nom",
    "chez des amis": "formule interne, à laisser dire aux clients",
    "baignade": "ne pas parler de baignade (le lac est interdit à la baignade)",
    "se baigner": "ne pas parler de baignade",
    "swimming": "ne pas parler de baignade",
    "écrin": "mot à éviter",
    "havre de paix": "mot à éviter",
    "n’hésitez pas": "formule à éviter",
}
# Indices de français oublié sur une page anglaise
FRENCH_HINTS = [" le château ", " les ", " avec ", " pour ", " nous ", " vous ", "Réserver", "Demander un devis", " dès "]

def pages():
    for lang, table in (("fr", B.PAGES), ("en", B.PAGES_EN)):
        for view, (folder, title, desc) in table.items():
            f = ROOT / folder / "index.html" if folder else ROOT / "index.html"
            yield lang, view, folder, title, desc, f

def visible_text(h):
    h = re.sub(r"<(script|style)\b.*?</\1>", " ", h, flags=re.S)
    h = re.sub(r'<div class="util-bar.*?</div>\s*</div>', " ", h, flags=re.S)  # bandeau de maquette
    h = re.sub(r'<blockquote lang="fr">.*?</blockquote>', " ", h, flags=re.S)  # avis clients cités en français
    return html.unescape(re.sub(r"<[^>]+>", " ", h))

def check_static():
    src = (ROOT / "src" / "site.html").read_text(encoding="utf-8")
    # 1. Les pages générées sont à jour
    newest_src = max(p.stat().st_mtime for p in [ROOT / "src/site.html", ROOT / "tools/build_pages.py", ROOT / "css/site.css", ROOT / "js/site.js"])
    for lang, view, folder, title, desc, f in pages():
        if not f.exists():
            err(folder or "/", "page absente : relancer tools/build_pages.py"); continue
        if f.stat().st_mtime < newest_src - 1:
            err(folder or "/", "page plus ancienne que la source : relancer tools/build_pages.py")
    # 2. Chaque texte a sa traduction
    legal = [(mm.start(), src.find('<div class="view"', mm.start() + 10) if src.find('<div class="view"', mm.start() + 10) > 0 else len(src))
             for mm in re.finditer(r'<div class="view" data-view="(mentions|confidentialite)"', src)]
    for m in re.finditer(r"<(h[1-6]|p|li|a|button|summary|span|b|small|label|option|th|td|dt)\b([^>]*)>([^<]{3,})</\1>", src):
        if any(a <= m.start() < b for a, b in legal) or 'lang="fr"' in m.group(2):
            continue
        line_start = src.rfind("\n", 0, m.start()) + 1
        if "data-en=" in src[line_start:m.start()] or 'lang="fr"' in src[line_start:m.start()]:
            continue  # texte à l’intérieur d’un bloc déjà traduit, ou citation en français
        attrs, txt = m.group(2), m.group(3).strip()
        if "data-en" in attrs or not re.search(r"[a-zà-ÿ]{3}", txt, re.I):
            continue
        if re.search(r"[éèêàùçô]|\b(le|la|les|des|une|pour|avec|vous|nous)\b", txt, re.I):
            line = src[:m.start()].count("\n") + 1
            warn("src/site.html:%d" % line, "texte sans traduction anglaise (data-en) : « %s »" % txt[:60])
    # 3. Contrôles page par page
    seen_titles, seen_desc = {}, {}
    for lang, view, folder, title, desc, f in pages():
        if not f.exists():
            continue
        name = "/" + (folder + "/" if folder else "")
        h = f.read_text(encoding="utf-8")
        head = h[:h.index("</head>")]
        if not (20 <= len(title) <= 70): warn(name, "titre de %d caractères (viser 30-65)" % len(title))
        if not (70 <= len(desc) <= 165): warn(name, "description de %d caractères (viser 110-160)" % len(desc))
        if title in seen_titles: err(name, "même titre que " + seen_titles[title])
        if desc in seen_desc: err(name, "même description que " + seen_desc[desc])
        seen_titles[title] = name; seen_desc[desc] = name
        if not re.search(r'<html lang="%s"' % lang, h): err(name, "attribut lang absent ou faux")
        for tag in ['rel="canonical"', 'hreflang="fr"', 'hreflang="en"', 'hreflang="x-default"', 'og:title', 'og:description', 'og:image"', 'og:image:alt', 'og:url', 'twitter:card']:
            if tag not in head: err(name, "balise manquante : " + tag)
        m = re.search(r'og:image" content="[^"]*?/(images/[^"]+)"', head)
        if m:
            img = ROOT / m.group(1)
            if not img.exists():
                err(name, "image de partage introuvable : " + m.group(1))
            else:
                try:
                    from PIL import Image
                    w, hh = Image.open(img).size
                    if (w, hh) != (1200, 630): warn(name, "image de partage %dx%d (attendu 1200x630)" % (w, hh))
                except ImportError:
                    pass
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try: json.loads(block)
            except Exception as e: err(name, "données structurées invalides : %s" % e)
        if '<details class="faq-item">' in h and '"FAQPage"' not in h: err(name, "FAQ visible mais pas de FAQPage dans les données structurées")
        n_h1 = len(re.findall(r"<h1\b", h))
        if n_h1 != 1: err(name, "%d titres h1 (il en faut 1)" % n_h1)
        if 'class="view"' in h and len(re.findall(r'class="view"', h)) > 1: err(name, "plusieurs vues dans la page")
        if "data-en=" in h: err(name, "attribut data-en resté dans la page générée")
        for im in re.findall(r"<img\b[^>]*>", h):
            if 'alt="' not in im: err(name, "image sans texte alternatif : " + im[:80])
        txt = visible_text(h)
        low = txt.lower()
        for word, why in BANNED.items():
            if word.lower() in low and not (view in ("mentions", "confidentialite")):
                err(name, "mot interdit « %s » (%s)" % (word, why))
        if "happy shelter" in low and view not in ("mentions", "confidentialite"):
            err(name, "« Happy Shelter » hors des mentions légales")
        if lang == "en" and view not in ("mentions", "confidentialite"):
            body = txt
            for hint in FRENCH_HINTS:
                if hint in body:
                    warn(name, "possible texte français sur la page anglaise : « %s »" % hint.strip())
        if lang == "en" and re.search(r'alt="[^"]*\b(le|la|les|du|des|une|sous|avec|sur)\b[^"]*"', h) and view not in ("mentions", "confidentialite"):
            warn(name, "texte alternatif en français sur la page anglaise (ajouter la traduction dans ATTR_EN de build_pages.py)")
    # 4. Plan du site, robots, llms.txt
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for lang, view, folder, *_ in pages():
        url = B.DOMAIN + "/" + (folder + "/" if folder else "")
        if "<loc>%s</loc>" % url not in sm: err("sitemap.xml", "adresse absente : " + url)
    llms = ROOT / "llms.txt"
    if not llms.exists():
        err("llms.txt", "fichier absent")
    else:
        lt = llms.read_text(encoding="utf-8")
        for view, (folder, *_ ) in B.PAGES.items():
            if view in ("mentions", "confidentialite"): continue
            url = B.DOMAIN + "/" + (folder + "/" if folder else "")
            if url + ")" not in lt: warn("llms.txt", "page non citée : " + url)
        flat = re.sub(r"[\u00a0\u202f]", " ", src)
        for price in re.findall(r"(\d[\d \u00a0\u202f]*\d|\d+) €", lt):
            p = re.sub(r"[\u00a0\u202f]", " ", price).strip()
            if p not in flat:
                warn("llms.txt", "prix « %s € » absent du site : vérifier qu’il est à jour" % p)
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8") if (ROOT / "robots.txt").exists() else ""
    if re.search(r"^Disallow:\s*/\s*$", robots, re.M):
        err("robots.txt", "le site est bloqué aux moteurs (« Disallow: / ») alors qu'il est en ligne")
    if "Sitemap: " + B.DOMAIN + "/sitemap.xml" not in robots:
        err("robots.txt", "ligne « Sitemap: %s/sitemap.xml » absente" % B.DOMAIN)
    if re.search(r'<meta name="robots" content="[^"]*noindex', src):
        err("src/site.html", "balise noindex présente : le site serait retiré de Google")
    if not (ROOT / "_redirects").exists():
        warn("_redirects", "fichier absent : les anciennes adresses Wix ne sont plus redirigées")

def port_free(p):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", p)) != 0

def check_browser():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        warn(None, "playwright absent : vérification d’affichage non faite (pip install playwright && playwright install chromium)")
        return
    port = 8790
    while not port_free(port): port += 1
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port)], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    JS = r"""() => {
      const roots=[document.querySelector('header'),document.querySelector('main'),document.querySelector('footer')].filter(Boolean);
      const leaves=[];
      roots.forEach(r=>r.querySelectorAll('*').forEach(el=>{
        if(el.closest('[hidden],details:not([open]) > p,.faq-item:not([open]) p')) return;
        const cs=getComputedStyle(el); if(cs.visibility==='hidden'||cs.display==='none'||+cs.opacity===0) return;
        for(let a=el;a;a=a.parentElement){const r=a.getBoundingClientRect(); if(r.width<=1||r.height<=1) return;}
        const hasText=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1);
        if(!hasText) return;
        const range=document.createRange(); range.selectNodeContents(el);
        const rects=[...range.getClientRects()].filter(r=>r.width>1&&r.height>1);
        if(rects.length) leaves.push({el,rects,txt:el.textContent.trim().slice(0,40)});
      }));
      const out=[];
      for(let i=0;i<leaves.length;i++)for(let j=i+1;j<leaves.length;j++){
        const A=leaves[i],B=leaves[j]; if(A.el.contains(B.el)||B.el.contains(A.el)) continue;
        let hit=false;
        for(const a of A.rects){for(const b of B.rects){const w=Math.min(a.right,b.right)-Math.max(a.left,b.left),h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top); if(w>3&&h>3){hit=true;break}} if(hit)break;}
        if(hit) out.push('textes superposés : « '+A.txt+' » / « '+B.txt+' »');
      }
      leaves.forEach(L=>{const el=L.el,cs=getComputedStyle(el); if(el.scrollWidth>el.clientWidth+3&&cs.display!=='inline'&&el.clientWidth>1&&cs.overflow!=='hidden') out.push('texte qui déborde : « '+L.txt+' »');});
      if(document.documentElement.scrollWidth>innerWidth+2) out.push('défilement horizontal ('+document.documentElement.scrollWidth+' px pour '+innerWidth+')');
      return out;
    }"""
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for w in (1440, 1180, 1024, 768, 390, 340):
                pg = b.new_page(viewport={"width": w, "height": 900})
                js_errors = []
                pg.on("pageerror", lambda e: js_errors.append(str(e)))
                for lang, view, folder, *_ in pages():
                    url = "http://127.0.0.1:%d/%s" % (port, (folder + "/") if folder else "")
                    resp = pg.goto(url)
                    if resp.status != 200: err("/" + folder, "HTTP %d" % resp.status); continue
                    pg.wait_for_timeout(150)
                    for msg in pg.evaluate(JS):
                        err("/%s (%d px)" % (folder + "/" if folder else "", w), msg)
                    if w == 1440:
                        broken = pg.evaluate("""() => [...document.images].filter(i=>i.complete&&i.naturalWidth===0&&!i.src.includes('sirvoy')).map(i=>i.getAttribute('src'))""")
                        for s in broken: err("/" + folder, "image cassée : " + s)
                for e in js_errors: err("JavaScript (%d px)" % w, e)
                pg.close()
            b.close()
    finally:
        srv.terminate()

if __name__ == "__main__":
    check_static()
    if "--static" not in sys.argv:
        check_browser()
    for w in warnings: print("AVERTISSEMENT  " + w)
    for e in errors: print("ERREUR         " + e)
    print("\n%d erreur(s), %d avertissement(s)" % (len(errors), len(warnings)))
    sys.exit(1 if errors else 0)
