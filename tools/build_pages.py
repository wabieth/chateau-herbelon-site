#!/usr/bin/env python3
"""Génère une page HTML par vue à partir de src/site.html.

Chaque vue du site (#seminaires, #mariages…) devient une vraie adresse
(/seminaires/, /mariages/…) avec son titre, sa description et son adresse
canonique, pour que Google et les IA voient chaque page.
À relancer après chaque modification de src/site.html :
    python3 tools/build_pages.py
"""
import json, re, pathlib, html as html_lib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "site.html"
DOMAIN = "https://www.chateaudherbelon.com"
OG_IMAGE = "images/chateau-automne.jpg"
# image de partage (1200 x 630) et sa description, par page
OG = {
    "accueil": ("images/og/accueil.jpg", "La tourelle couverte de lierre du Château d’Herbelon, au-dessus du lac turquoise de Monteynard"),
    "seminaires": ("images/og/seminaires.jpg", "La terrasse abritée du château, tables dressées face au lac de Monteynard"),
    "mariages": ("images/og/mariages.jpg", "Une cérémonie installée sur la pelouse du château, face aux montagnes"),
    "ete": ("images/og/ete.jpg", "Kitesurfs et wingfoils sur le lac de Monteynard, en contrebas du château"),
    "restaurant": ("images/og/restaurant.jpg", "La guinguette du château un soir d’été, face au lac"),
    "proches": ("images/og/proches.jpg", "Le château à la tombée du jour, la tourelle éclairée"),
    "retraites": ("images/og/retraites.jpg", "Le lac de Monteynard au crépuscule, très calme"),
    "chateau": ("images/og/chateau.jpg", "La façade du Château d’Herbelon en automne"),
    "contact": ("images/og/contact.jpg", "Le Château d’Herbelon vu du ciel, le parc et le lac"),
    "mentions": ("images/og/accueil.jpg", "Le Château d’Herbelon au-dessus du lac de Monteynard"),
    "confidentialite": ("images/og/accueil.jpg", "Le Château d’Herbelon au-dessus du lac de Monteynard"),
}

# vue -> (dossier, titre, description)
PAGES = {
    "accueil": ("", "Château d’Herbelon, au bord du lac de Monteynard",
        "Château de plus de 400 ans à 40 min de Grenoble. Séminaires, mariages, retraites ; l’été : hôtel, restaurant et guinguette au bord du lac."),
    "seminaires": ("seminaires", "Séminaire au bord du lac, à 40 min de Grenoble · Château d’Herbelon",
        "Le château entier pour votre équipe, de 10 à 100 personnes. Journée d’étude dès 85 € HT, résidentiel dès 210 € HT. Devis sous 48 h."),
    "mariages": ("mariages", "Mariage dans un château au bord du lac, Isère · Château d’Herbelon",
        "Le château à vous tout le week-end, jusqu’à 100 invités, 39 couchages. Dès 4 500 € en hiver. De septembre à juin, hiver compris."),
    "ete": ("ete", "Hôtel au bord du lac de Monteynard, juillet-août · Château d’Herbelon",
        "13 chambres dans un château au bord du lac, restaurant et guinguette. Paddle, voile et wingfoil à deux pas. Animaux bienvenus."),
    "restaurant": ("restaurant", "Restaurant face au lac de Monteynard · Château d’Herbelon",
        "En juillet et août, tous les jours : la carte de notre chef sur la terrasse, un verre à la guinguette. Réservation par téléphone."),
    "proches": ("entre-proches", "Louer un château pour un week-end en famille · Château d’Herbelon",
        "Le château rien qu’à vous, en famille ou entre amis : 39 couchages, le parc, le lac. Jusqu’à 50 personnes, dès 3 200 € le week-end."),
    "retraites": ("retraites", "Lieu de retraite privatisé au bord d’un lac · Château d’Herbelon",
        "Aucun autre client, salle de pratique de 6 h à 22 h, repas végétariens. Dès 120 € par personne et par nuit, 16 personnes minimum."),
    "chateau": ("le-chateau", "Le château : histoire, chambres, accès · Château d’Herbelon",
        "Plus de 400 ans d’histoire au bord du lac de Monteynard, 13 chambres chacune avec sa salle de bain, à 40 min de Grenoble par l’A51."),
    "contact": ("contact", "Contact et devis · Château d’Herbelon",
        "Une date, un projet ? Écrivez-nous ou appelez le 04 58 00 88 95. On vous répond dans la journée, et on envoie un devis d’une page sous 48 h."),
    "mentions": ("mentions-legales", "Mentions légales · Château d’Herbelon",
        "Éditeur, hébergeur et informations légales du site du Château d’Herbelon."),
    "confidentialite": ("confidentialite", "Politique de confidentialité · Château d’Herbelon",
        "Comment le Château d’Herbelon traite les données envoyées par le formulaire de contact. Aucun cookie publicitaire ni de mesure d’audience."),
}

ASSET = re.compile(r'((?:src|href|poster|data-src|data-src-mobile|data-poster-end)=")((?:css|js|images|fonts)/[^"]*|favicon\.ico(?:\?[^"]*)?|apple-touch-icon\.png(?:\?[^"]*)?|site\.webmanifest)"')

JSONLD = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": ["Hotel", "EventVenue"],
            "@id": DOMAIN + "/#chateau",
            "name": "Château d’Herbelon",
            "description": "Château de plus de 400 ans au bord du lac de Monteynard, à 40 minutes au sud de Grenoble. De septembre à juin, privatisé pour des séminaires, mariages, retraites et week-ends entre proches, de 10 à 100 personnes. En juillet et août : hôtel, restaurant et guinguette ouverts à tous.",
            "url": DOMAIN + "/",
            "telephone": "+33 4 58 00 88 95",
            "email": "contact@chateaudherbelon.com",
            "address": {"@type": "PostalAddress", "streetAddress": "1605 route d’Herbelon", "postalCode": "38650", "addressLocality": "Treffort", "addressRegion": "Isère", "addressCountry": "FR"},
            "geo": {"@type": "GeoCoordinates", "latitude": 44.898078, "longitude": 5.674102},
            "image": [DOMAIN + "/images/og/accueil.jpg", DOMAIN + "/images/chateau-lac.jpg", DOMAIN + "/images/mariage-ceremonie.jpg", DOMAIN + "/images/salon.jpg", DOMAIN + "/images/lac-voiles.jpg"],
            "logo": DOMAIN + "/images/logo-herbelon.svg",
            "numberOfRooms": 13,
            "checkinTime": "15:00",
            "checkoutTime": "11:00",
            "maximumAttendeeCapacity": 100,
            "petsAllowed": True,
            "priceRange": "€€",
            "amenityFeature": [
                {"@type": "LocationFeatureSpecification", "name": "Accès au lac de Monteynard", "value": True},
                {"@type": "LocationFeatureSpecification", "name": "Parc", "value": True},
                {"@type": "LocationFeatureSpecification", "name": "Salle de bain dans chaque chambre", "value": True},
                {"@type": "LocationFeatureSpecification", "name": "Salles de séminaire", "value": True},
                {"@type": "LocationFeatureSpecification", "name": "Parking gratuit", "value": True}
            ],
            "sameAs": ["https://www.instagram.com/chateaudherbelon/", "https://www.facebook.com/Chateaudherbelon/"]
        },
        {
            "@type": "Restaurant",
            "@id": DOMAIN + "/restaurant/#restaurant",
            "name": "Restaurant et guinguette du Château d’Herbelon",
            "url": DOMAIN + "/restaurant/",
            "telephone": "+33 4 58 00 88 95",
            "servesCuisine": "Cuisine française de saison, produits locaux",
            "acceptsReservations": "Par téléphone",
            "address": {"@type": "PostalAddress", "streetAddress": "1605 route d’Herbelon", "postalCode": "38650", "addressLocality": "Treffort", "addressCountry": "FR"},
            "containedInPlace": {"@id": DOMAIN + "/#chateau"}
        }
    ]
}

def keep_view(html, view):
    starts = [m.start() for m in re.finditer(r'<div class="view" data-view="', html)]
    end_main = html.index("</main>")
    bounds = starts + [end_main]
    parts = [html[:starts[0]]]
    for i, st in enumerate(starts):
        block = html[st:bounds[i + 1]]
        name = re.match(r'<div class="view" data-view="([a-z]+)"', block).group(1)
        if name == view:
            parts.append(re.sub(r'^(<div class="view" data-view="[a-z]+") hidden>', r'\1>', block))
    parts.append(html[end_main:])
    return "".join(parts)

# pages anglaises : (dossier, titre, description)
PAGES_EN = {
    "accueil": ("en", "Château d’Herbelon, a château on Lake Monteynard near Grenoble",
        "A 400-year-old château 40 minutes from Grenoble. Offsites, weddings and retreats; in summer, a hotel, restaurant and guinguette by the lake."),
    "seminaires": ("en/offsites", "Team offsite by a lake, 40 min from Grenoble · Château d’Herbelon",
        "The whole château for your team, 10 to 100 people. Day package from €85 excl. VAT, overnight from €210. One-page quote within 48 hours."),
    "mariages": ("en/weddings", "Lakeside château wedding venue, French Alps · Château d’Herbelon",
        "The château for the whole weekend, up to 100 guests, sleeps 39. From €4,500 in winter. Weddings from September to June."),
    "ete": ("en/summer", "Château hotel on Lake Monteynard, July–August · Château d’Herbelon",
        "13 rooms in a château above the lake, restaurant and guinguette. Kitesurfing, wing foiling and paddleboarding next door. Pets welcome."),
    "restaurant": ("en/restaurant", "Restaurant and guinguette facing Lake Monteynard · Château d’Herbelon",
        "Every day in July and August: our chef’s menu on the terrace and drinks at the guinguette, open to everyone. Book by phone."),
    "proches": ("en/family-weekends", "Rent a château for a family weekend near Grenoble · Château d’Herbelon",
        "The château all to yourselves with family or friends: sleeps 39, grounds running down to the lake. Up to 50 people, from €3,200 a weekend."),
    "retraites": ("en/retreats", "Exclusive-use retreat venue on a lake in the Alps · Château d’Herbelon",
        "No other guests, a practice room open 6 am to 10 pm, vegetarian meals. From €120 per person per night, minimum 16 people."),
    "chateau": ("en/the-chateau", "The château: history, bedrooms, getting here · Château d’Herbelon",
        "Over 400 years of history on Lake Monteynard, 13 bedrooms each with its own bathroom, 40 minutes from Grenoble on the A51."),
    "contact": ("en/contact", "Contact and quotes · Château d’Herbelon",
        "A date or a project in mind? Write to us or call +33 4 58 00 88 95. We reply the same day and send a one-page quote within 48 hours."),
    "mentions": ("en/legal-notice", "Legal notice · Château d’Herbelon",
        "Publisher, host and legal information for the Château d’Herbelon website (in French)."),
    "confidentialite": ("en/privacy", "Privacy policy · Château d’Herbelon",
        "How the Château d’Herbelon handles data sent through the contact form. No advertising or analytics cookies (in French)."),
}

OG_ALT_EN = {
    "accueil": "The ivy-covered turret of Château d’Herbelon above turquoise Lake Monteynard",
    "seminaires": "The château’s covered terrace, tables laid facing Lake Monteynard",
    "mariages": "A wedding ceremony set up on the château lawn, facing the mountains",
    "ete": "Kitesurfers and wing foilers on Lake Monteynard below the château",
    "restaurant": "The château’s guinguette on a summer evening, facing the lake",
    "proches": "The château at dusk, the turret lit up",
    "retraites": "Lake Monteynard at dusk, perfectly still",
    "chateau": "The façade of Château d’Herbelon in autumn",
    "contact": "Château d’Herbelon from the air, the grounds and the lake",
    "mentions": "Château d’Herbelon above Lake Monteynard",
    "confidentialite": "Château d’Herbelon above Lake Monteynard",
}

# textes alternatifs et libellés d'accessibilité, traduits pour les pages anglaises
ATTR_EN = {
    "Deux fauteuils en rotin sur la pelouse, une guirlande « Just married » tendue devant le portail ouvert sur le lac": "Two rattan armchairs on the lawn, a “Just married” banner across the gate that opens onto the lake",
    "Deux transats sur la pelouse, le portail ouvert sur le lac turquoise": "Two deckchairs on the lawn, the gate open onto the turquoise lake",
    "Kitesurfs et wingfoils sur le lac turquoise, un après-midi de vent": "Kitesurfers and wing foilers on the turquoise lake on a windy afternoon",
    "La façade du château en automne, la vigne vierge rouge sur la tourelle": "The château façade in autumn, red Virginia creeper on the turret",
    "La façade en automne, la vigne vierge rouge, des amis devant la porte": "The façade in autumn with red Virginia creeper, friends by the door",
    "La guinguette un soir d’été, tables sous la tonnelle face au lac": "The guinguette on a summer evening, tables under the pergola facing the lake",
    "La terrasse abritée face au lac, pour les pauses et les déjeuners": "The covered terrace facing the lake, for breaks and lunches",
    "La terrasse au petit matin, la brume sur le lac et les sommets au loin": "The terrace at dawn, mist on the lake and peaks in the distance",
    "La tourelle du château couverte de lierre, le lac au loin": "The château’s ivy-covered turret, the lake in the distance",
    "Le Trièves vu du ciel : prairies, forêts, le lac et les sommets au loin": "The Trièves from the air: meadows, forests, the lake and distant peaks",
    "Le château à la tombée du jour, la tourelle éclairée, le portail ouvert sur le lac": "The château at dusk, the turret lit up, the gate open onto the lake",
    "Le grand salon et sa cheminée monumentale, tables installées sous le plafond en bois": "The grand drawing room with its huge fireplace, tables set under the wooden ceiling",
    "Le grand salon : plafond à la française, cheminée monumentale en pierre et tables dressées": "The grand drawing room: beamed ceiling, huge stone fireplace and laid tables",
    "Le lac au crépuscule, les sommets rosés au loin": "The lake at dusk, pink peaks in the distance",
    "Le lac de Monteynard couvert d’ailes et de voiles, un après-midi d’été": "Lake Monteynard full of kites and sails on a summer afternoon",
    "Le lac de Monteynard en automne, les sommets enneigés au fond": "Lake Monteynard in autumn, snowy peaks behind",
    "Le salon au plafond à la française": "The drawing room with its beamed ceiling",
    "Les caves voûtées du château, éclairées par le bas": "The château’s vaulted cellars, lit from below",
    "L’entrée du domaine : l’allée de gravier mène au château et à sa tourelle, sous les branches d’un sapin": "The entrance to the estate: a gravel drive leads to the château and its turret, under fir branches",
    "Un chien regarde le lac depuis le muret du parc": "A dog looks out over the lake from the garden wall",
    "Un cocktail préparé au bar, garni d’une feuille fraîche": "A cocktail made at the bar, garnished with a fresh leaf",
    "Un lit double sous la pente du toit, murs rouge profond, lampes de chevet allumées": "A double bed under the sloping roof, deep red walls, bedside lamps on",
    "Un lit sous un ciel de lit rose, coussins en toile de Jouy": "A bed under a pink canopy with toile de Jouy cushions",
    "Un serveur sort du château sous le lierre, plateau à la main, un soir d’été": "A waiter steps out of the château under the ivy, tray in hand, on a summer evening",
    "Une chambre au lit à baldaquin jaune et gris, sol en tomettes anciennes": "A bedroom with a yellow and grey four-poster bed and old terracotta tiles",
    "Une chambre lumineuse : mur en galets, lit double, coin salon": "A bright bedroom: pebble-stone wall, double bed, sitting area",
    "Une chambre lumineuse avec un mur en galets, un lit double et un coin salon": "A bright bedroom with a pebble-stone wall, a double bed and a sitting area",
    "Une chambre sous les toits avec un canapé, un fauteuil et deux lucarnes": "An attic bedroom with a sofa, an armchair and two dormer windows",
    "Une chambre sous les toits avec un ciel de lit vert et or et un bureau ancien": "An attic bedroom with a green and gold canopy and an antique desk",
    "Une chambre sous les toits, deux fauteuils devant une grande fenêtre ouverte sur les arbres": "An attic bedroom, two armchairs by a large window open onto the trees",
    "Une cérémonie de mariage installée sur la pelouse du château": "A wedding ceremony set up on the château lawn",
    "Une cérémonie installée sur la pelouse du château : deux fauteuils en rotin, les rangées de chaises, les invités devant la façade": "A ceremony set up on the château lawn: two rattan armchairs, rows of chairs, guests by the façade",
    "Une grande table dressée dans la salle à manger du château, devant les fenêtres à petits carreaux": "A long table laid in the château dining room, in front of small-paned windows",
    "Une vacancière travaille sur son ordinateur sous la pergola, face au lac couvert de voiles": "A guest works on her laptop under the pergola, facing a lake full of sails",
    "La salle de bain de la chambre Magnolia : carreaux bleu-gris, douche derrière une verrière, double vasque ancienne sur pieds en laiton": "The Magnolia room’s bathroom: blue-grey tiles, a walk-in shower behind glass, a vintage double basin on brass legs",
    "Un salon du château : boiseries, rideaux dorés et fenêtres à petits carreaux ouvertes sur le lac": "A drawing room in the château: wood panelling, golden curtains and small-paned windows open onto the lake",
    "Aperçu selon la saison": "Seasonal preview",
    "Château d’Herbelon, accueil": "Château d’Herbelon, home",
    "Menu": "Menu",
    "Navigation principale": "Main navigation",
}

def find_close(html, tag, pos):
    """Position de la balise fermante correspondant à <tag> ouverte juste avant pos."""
    depth = 1
    pat = re.compile(r'<(/?)%s\b[^>]*>' % tag)
    for m in pat.finditer(html, pos):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.start(), m.end()
    raise ValueError("balise non fermée : " + tag)

OPEN_EN = re.compile(r'<([a-z0-9]+)\b([^>]*?)\sdata-en="([^"]*)"([^>]*)>')

def apply_lang(html, lang):
    """Écrit chaque texte dans la langue de la page et retire les attributs data-en."""
    out, i = [], 0
    while True:
        m = OPEN_EN.search(html, i)
        if not m:
            out.append(html[i:]); break
        tag, before, en, after = m.group(1), m.group(2), m.group(3), m.group(4)
        out.append(html[i:m.start()])
        out.append("<%s%s%s>" % (tag, before, after))
        cs, ce = find_close(html, tag, m.end())
        inner = html[m.end():cs]
        if lang == "en":
            inner = en.replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&")
        out.append(inner)
        i = cs  # le reste (fermeture comprise) est traité au tour suivant
    return "".join(out)

LANG_BLOCK = re.compile(r'<div class="lang" role="group" aria-label="Langue / Language">.*?</div>', re.S)

def faq_jsonld(html):
    items = re.findall(r'<details class="faq-item"><summary>(.*?)</summary><p>(.*?)</p></details>', html, re.S)
    if not items:
        return None
    clean = lambda t: html_lib.unescape(re.sub(r"<[^>]+>", "", t)).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": clean(q), "acceptedAnswer": {"@type": "Answer", "text": clean(a)}} for q, a in items]}

def build():
    html = SRC.read_text(encoding="utf-8")
    # versions des feuilles de style et du script : le navigateur recharge quand le fichier change
    import hashlib
    for asset in ("css/site.css", "css/fonts.css", "js/site.js"):
        h = hashlib.sha1((ROOT / asset).read_bytes()).hexdigest()[:8]
        html = html.replace('"%s"' % asset, '"%s?v=%s"' % (asset, h))
    url_of = lambda lang, v: DOMAIN + "/" + (((PAGES if lang == "fr" else PAGES_EN)[v][0] + "/") if (PAGES if lang == "fr" else PAGES_EN)[v][0] else "")
    count = 0
    for lang, table in (("fr", PAGES), ("en", PAGES_EN)):
        for view, (folder, title, desc) in table.items():
            depth = folder.count("/") + 1 if folder else 0
            root = "../" * depth
            out = keep_view(html, view)
            out = apply_lang(out, lang)
            def link(v, t=table):
                f = t[v][0]
                return (root + f + "/") if f else (root or "./")
            def repl_topic(m):
                return 'href="%s?sujet=%s" data-topic="%s"' % (link("contact"), m.group(1), m.group(1))
            out = re.sub(r'href="#contact" data-topic="([a-z]+)"', repl_topic, out)
            out = out.replace('href="#reserver-ete"', 'href="%s#reserver"' % link("ete"))
            for v in table:
                out = out.replace('href="#%s"' % v, 'href="%s"' % link(v))
            # sélecteur de langue : un lien vers la même page dans l’autre langue
            fr_href, en_href = link(view, PAGES), link(view, PAGES_EN)
            cur = lambda l: ' aria-current="page"' if l == lang else ''
            out = LANG_BLOCK.sub('<nav class="lang" aria-label="Langue / Language"><a href="%s" hreflang="fr" lang="fr"%s>FR</a><a href="%s" hreflang="en" lang="en"%s>EN</a></nav>' % (fr_href, cur("fr"), en_href, cur("en")), out, count=1)
            if lang == "en":
                norm = lambda x: x.replace("\u00a0", " ").replace("\u202f", " ")
                attr_en = {norm(k): v for k, v in ATTR_EN.items()}
                out = re.sub(r'(alt|aria-label)="([^"]*)"', lambda m: '%s="%s"' % (m.group(1), attr_en.get(norm(m.group(2)), m.group(2))), out)
            if depth:
                out = ASSET.sub(lambda m: m.group(1) + root + m.group(2) + '"', out)
            url = url_of(lang, view)
            out = out.replace('<html lang="fr"', '<html lang="%s" data-page="%s" data-root="%s"' % (lang, view, root or "./"), 1)
            out = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, out, count=1)
            out = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc, out, count=1)
            og_img, og_alt = OG[view]
            if lang == "en":
                og_alt = OG_ALT_EN[view]
            ld = json.loads(json.dumps(JSONLD))
            if lang == "en":
                for node in ld["@graph"]:
                    if node.get("@id", "").endswith("#chateau"):
                        node["description"] = "A château over 400 years old on Lake Monteynard, 40 minutes south of Grenoble, France. From September to June it is booked whole for offsites, weddings, retreats and family weekends, for 10 to 100 people. In July and August: hotel, restaurant and guinguette open to all."
            blocks = [ld]
            fq = faq_jsonld(out)
            if fq:
                blocks.append(fq)
            ld_tags = "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(b, ensure_ascii=False) for b in blocks)
            head = ('<link rel="canonical" href="%s">\n'
                    '<link rel="alternate" hreflang="fr" href="%s">\n'
                    '<link rel="alternate" hreflang="en" href="%s">\n'
                    '<link rel="alternate" hreflang="x-default" href="%s">\n'
                    '<meta property="og:type" content="website">\n'
                    '<meta property="og:site_name" content="Château d’Herbelon">\n'
                    '<meta property="og:title" content="%s">\n'
                    '<meta property="og:description" content="%s">\n'
                    '<meta property="og:url" content="%s">\n'
                    '<meta property="og:image" content="%s/%s">\n'
                    '<meta property="og:image:width" content="1200">\n'
                    '<meta property="og:image:height" content="630">\n'
                    '<meta property="og:image:alt" content="%s">\n'
                    '<meta property="og:locale" content="%s">\n'
                    '<meta property="og:locale:alternate" content="%s">\n'
                    '<meta name="twitter:card" content="summary_large_image">\n'
                    '<meta name="twitter:title" content="%s">\n'
                    '<meta name="twitter:description" content="%s">\n'
                    '<meta name="twitter:image" content="%s/%s">\n'
                    ) % (url, url_of("fr", view), url_of("en", view), url_of("fr", view), title, desc, url, DOMAIN, og_img, og_alt,
                         "fr_FR" if lang == "fr" else "en_GB", "en_GB" if lang == "fr" else "fr_FR", title, desc, DOMAIN, og_img) + ld_tags
            out = out.replace("</head>", head + "</head>", 1)
            dest = ROOT / folder / "index.html" if folder else ROOT / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(out, encoding="utf-8")
            count += 1
    # plan du site, avec les deux langues
    rows = []
    for view in PAGES:
        for lang in ("fr", "en"):
            rows.append('  <url><loc>%s</loc><xhtml:link rel="alternate" hreflang="fr" href="%s"/><xhtml:link rel="alternate" hreflang="en" href="%s"/></url>\n' % (url_of(lang, view), url_of("fr", view), url_of("en", view)))
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "".join(rows) + "</urlset>\n", encoding="utf-8")
    print("ok :", count, "pages")

if __name__ == "__main__":
    build()
