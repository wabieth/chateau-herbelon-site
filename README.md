# Site du Château d'Herbelon

Site statique (HTML, CSS, JavaScript), sans étape de construction.
Hébergement prévu : Cloudflare Pages, connecté à ce dépôt.

- Commande de build : aucune
- Dossier de sortie : `/` (racine du dépôt)
- Branche de production : `main`

Le site est en phase de maquette : `robots.txt` et la balise `noindex` dans `index.html` empêchent son référencement. Les retirer le jour de la mise en ligne.

## Une adresse par page

Le site se modifie dans `src/site.html` (toutes les pages dans un seul fichier).
Après chaque modification, lancer :

    python3 tools/build_pages.py

Le script génère `index.html` (accueil) et un dossier par page (`seminaires/`, `mariages/`, `ete/`,
`restaurant/`, `entre-proches/`, `retraites/`, `le-chateau/`, `contact/`, `mentions-legales/`,
`confidentialite/`), chacun avec son titre, sa description, son adresse canonique et les données
structurées schema.org, ainsi que `sitemap.xml`. Les anciens liens en `#seminaires` redirigent vers la bonne page.
