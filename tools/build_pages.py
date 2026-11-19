#!/usr/bin/env python3
"""Génère une page HTML par vue à partir de src/site.html.

Chaque vue du site (#seminaires, #mariages…) devient une vraie adresse
(/seminaires/, /mariages/…) avec son titre, sa description et son adresse
canonique, pour que Google et les IA voient chaque page.
À relancer après chaque modification de src/site.html :
    python3 tools/build_pages.py
"""
import json, re, pathlib

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
        "Le château à vous tout le week-end, jusqu’à 100 invités, 35 couchages. Dès 4 500 € en hiver. De septembre à juin, hiver compris."),
    "ete": ("ete", "Hôtel au bord du lac de Monteynard, juillet-août · Château d’Herbelon",
        "13 chambres dans un château au bord du lac, restaurant et guinguette. Paddle, voile et wingfoil à deux pas. Animaux bienvenus."),
    "restaurant": ("restaurant", "Restaurant et guinguette face au lac de Monteynard · Château d’Herbelon",
        "En juillet et août, tous les jours : la carte de notre chef sur la terrasse, un verre à la guinguette. Réservation par téléphone."),
    "proches": ("entre-proches", "Louer un château pour un week-end en famille · Château d’Herbelon",
        "Le château rien qu’à vous, en famille ou entre amis : 35 couchages, le parc, le lac. Jusqu’à 50 personnes, dès 3 200 € le week-end."),
    "retraites": ("retraites", "Lieu de retraite privatisé au bord d’un lac, Alpes · Château d’Herbelon",
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

def build():
    html = SRC.read_text(encoding="utf-8")
    # versions des feuilles de style et du script : le navigateur recharge quand le fichier change
    import hashlib
    for asset in ("css/site.css", "css/fonts.css", "js/site.js"):
        h = hashlib.sha1((ROOT / asset).read_bytes()).hexdigest()[:8]
        html = html.replace('"%s"' % asset, '"%s?v=%s"' % (asset, h))
    for view, (folder, title, desc) in PAGES.items():
        depth = 1 if folder else 0
        root = "../" if depth else ""
        out = html
        # une seule vue par page : le contenu des autres pages n’est pas recopié (Google et les IA voient une page = un sujet)
        out = keep_view(out, view)
        # liens internes : #vue -> vraie adresse
        def link(v):
            f = PAGES[v][0]
            return (root + f + "/") if f else (root or "./")
        def repl_topic(m):
            return 'href="%s?sujet=%s" data-topic="%s"' % (link("contact"), m.group(1), m.group(1))
        out = re.sub(r'href="#contact" data-topic="([a-z]+)"', repl_topic, out)
        out = out.replace('href="#reserver-ete"', 'href="%s#reserver"' % link("ete"))
        for v in PAGES:
            out = out.replace('href="#%s"' % v, 'href="%s"' % link(v))
            out = out.replace('href=&quot;#%s&quot;' % v, 'href=&quot;%s&quot;' % link(v))
        # chemins des fichiers
        if depth:
            out = ASSET.sub(lambda m: m.group(1) + root + m.group(2) + '"', out)
        # en-tête : page, titre, description, canonique
        url = DOMAIN + "/" + (folder + "/" if folder else "")
        out = out.replace("<html lang=\"fr\"", "<html lang=\"fr\" data-page=\"%s\" data-root=\"%s\"" % (view, root or "./"), 1)
        out = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, out, count=1)
        out = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc, out, count=1)
        og_img, og_alt = OG[view]
        head = ('<link rel="canonical" href="%s">\n'
                '<meta property="og:type" content="website">\n'
                '<meta property="og:site_name" content="Château d’Herbelon">\n'
                '<meta property="og:title" content="%s">\n'
                '<meta property="og:description" content="%s">\n'
                '<meta property="og:url" content="%s">\n'
                '<meta property="og:image" content="%s/%s">\n'
                '<meta property="og:image:width" content="1200">\n'
                '<meta property="og:image:height" content="630">\n'
                '<meta property="og:image:alt" content="%s">\n'
                '<meta property="og:locale" content="fr_FR">\n'
                '<meta property="og:locale:alternate" content="en_GB">\n'
                '<meta name="twitter:card" content="summary_large_image">\n'
                '<meta name="twitter:title" content="%s">\n'
                '<meta name="twitter:description" content="%s">\n'
                '<meta name="twitter:image" content="%s/%s">\n'
                '<script type="application/ld+json">%s</script>\n') % (url, title, desc, url, DOMAIN, og_img, og_alt, title, desc, DOMAIN, og_img, json.dumps(JSONLD, ensure_ascii=False))
        out = out.replace("</head>", head + "</head>", 1)
        dest = ROOT / folder / "index.html" if folder else ROOT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
    # plan du site
    urls = "".join("  <url><loc>%s/%s</loc></url>\n" % (DOMAIN, (f + "/") if f else "") for f, _, _ in PAGES.values())
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n", encoding="utf-8")
    print("ok :", len(PAGES), "pages")

if __name__ == "__main__":
    build()
