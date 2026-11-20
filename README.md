# Site du Château d'Herbelon

Site statique (HTML, CSS, JavaScript), sans étape de construction.
Hébergement : Cloudflare (Worker avec fichiers statiques), connecté à ce dépôt.

- Commande de build : aucune
- Dossier de sortie : `/` (racine du dépôt)
- Branche de production : `main`

Le site est en production depuis le 20 novembre 2026 (www.chateaudherbelon.com). Les anciennes adresses Wix sont redirigées dans `_redirects`.

## Une adresse par page et par langue

Le site se modifie dans `src/site.html` (toutes les pages dans un seul fichier, chaque texte avec sa traduction `data-en`).
Après chaque modification :

    python3 tools/build_pages.py    # génère les pages françaises (/), anglaises (/en/) et sitemap.xml
    python3 tools/check_site.py     # vérifie SEO/GEO, traductions, affichage ; 0 erreur exigée

Les consignes complètes pour Claude sont dans `CLAUDE.md`. GitHub relance la vérification à chaque envoi (onglet Actions).
