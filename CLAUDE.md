# Site du Château d’Herbelon — consignes pour toute session Claude

Ce dépôt est le site du Château d’Herbelon (Treffort, lac de Monteynard). Il est publié par Cloudflare à chaque envoi sur GitHub.
Ces consignes valent pour **chaque modification**, même minime (une phrase, une photo, un prix).

## Après chaque modification : obligatoire

1. **Régénérer les pages** : `python3 tools/build_pages.py`
   Ne jamais modifier à la main `index.html`, `*/index.html`, `en/**` ni `sitemap.xml` : ils sont générés depuis `src/site.html`.
2. **Lancer la vérification** : `python3 tools/check_site.py`
   - Elle contrôle le SEO/GEO (titres, descriptions, canonique, hreflang, balises de partage, données structurées, FAQ, plan du site, llms.txt), les traductions, les mots interdits, les images, les erreurs JavaScript et l’affichage (textes superposés ou qui débordent) en français et en anglais, de 1440 à 340 px.
   - **0 erreur exigée** avant d’envoyer. Traiter aussi les avertissements, sauf le blocage robots.txt pendant la maquette.
   - Si Playwright manque : `pip install playwright pillow --break-system-packages && playwright install chromium`.
3. **Regarder** les pages touchées, en français ET en anglais, à 1440 px et 390 px (captures d’écran). La vérification automatique ne juge pas l’esthétique.
4. **Mettre à jour `llms.txt`** si un fait change (prix, capacité, horaires, services, conditions). C’est la fiche que lisent les IA.
5. **Envoyer** : commit avec un message en français, puis `git push`. GitHub relance la vérification (onglet Actions) ; si elle échoue, corriger tout de suite.
6. Dire à l’utilisateur ce qui a été vérifié et le résultat.

## Comment le site est construit

- **Source unique** : `src/site.html` contient toutes les vues (`<div class="view" data-view="…">`). `tools/build_pages.py` en fait une page par vue et par langue : `/seminaires/`, `/en/offsites/`, etc. Chaque page ne contient que sa vue.
- **Deux langues, deux adresses** : français à la racine, anglais sous `/en/`. Tout texte visible porte sa traduction dans `data-en="…"`. Les textes alternatifs d’images et les `aria-label` se traduisent dans `ATTR_EN` (dans `build_pages.py`). Sans traduction, le texte reste en français sur la page anglaise et la vérification le signale.
- **Nouvelle page** : l’ajouter dans `PAGES`, `PAGES_EN` et `OG` (dans `build_pages.py`), avec une image de partage 1200 × 630 dans `images/og/`, et dans `llms.txt`.
- **FAQ** : `<details class="faq-item"><summary data-en="…">Question</summary><p data-en="…">Réponse</p></details>` dans une `section.faq`. Les données structurées FAQPage sont générées automatiquement.
- **Données structurées** (Hotel, EventVenue, Restaurant) : `JSONLD` dans `build_pages.py`.
- **Feuilles de style et script** : `css/site.css`, `js/site.js`. Leurs adresses sont versionnées automatiquement, rien à faire contre le cache.
- **Réservation des chambres** : widget Sirvoy (formulaire 819bf40422ee1455), chargé uniquement sur la page L’été.
- **Formulaire de contact** : Web3Forms (clé dans `js/site.js`).

## Design : rester cohérent

- Direction « Domaine » : Cormorant Garamond (titres) et Instrument Sans (texte), pierre claire `#f5f3ee`, vert lierre `#1f3a2f`, lin `#e8dcc5` pour l’été, sauge `#e4e8df`, bleu lac `#2c7a80`. Ne pas ajouter de couleur ni de police.
- Réutiliser les classes existantes (`section`, `split`, `stack`, `arch`, `photo`, `carte`, `checks`, `cta-band`…) plutôt que d’en inventer.
- Photos : 2000 px de large au plus, moins de 600 Ko. Vidéos : H.264, moins de 25 Mo (limite Cloudflare), en boucle silencieuse avec bouton pause (`.loop-media`).

## Contenu : décisions prises avec Étienne (propriétaire)

- Prix : la grille Google Sheets d’Étienne fait foi. Toujours « à partir de » ; hors taxes pour les séminaires ; jamais de prix sur l’accueil.
- Delphine est la directrice : elle répond et accueille. Le chef n’est pas nommé (« notre chef ») tant qu’il n’est pas confirmé.
- Ne jamais parler de baignade (le lac est interdit à la baignade).
- Mariages : repas uniquement par notre chef (pas de traiteur extérieur pour l’instant), fête jusqu’à 4 h, acompte de 30 %.
- Nom unique : « Château d’Herbelon ». « HAPPY SHELTER HERBELON » seulement dans les mentions légales. Plus de coliving ni de coworking.
- Hôtel non classé : n’afficher aucune étoile.
- Ton : direct, concret, chaleureux, vouvoiement. Mots à éviter : niché, écrin, havre de paix, cadre exceptionnel, unique, prestigieux, magique, « n’hésitez pas », « chez des amis ».
- Ne jamais publier l’adresse e-mail personnelle d’Étienne : seulement contact@chateaudherbelon.com.
- Le positionnement complet est dans le projet Claude « Chateau d’Herbelon » (`claude/positionnement-externe.md`).

## Au lancement sur www.chateaudherbelon.com

Retirer `<meta name="robots" content="noindex, nofollow">` de `src/site.html` et le `Disallow: /` de `robots.txt` (ajouter la ligne `Sitemap:`), retirer le bandeau de maquette, rediriger les anciennes adresses Wix en 301, déclarer le site dans Google Search Console.
