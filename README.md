# BEBB News

Dieses öffentliche Repository enthält nur freigegebene Meldungen der Basler
Edition der Bernoulli-Briefwechsel und die dazugehörigen Bilder. Entwürfe
bleiben lokal: Schon ein Push in dieses Repository macht die Dateien öffentlich.

## Eine Meldung auf der BEBB-Startseite veröffentlichen

1. Die freigegebene TEI-Datei in `posts/` ablegen. Der Beitrag braucht eine
   eindeutige `xml:id`, einen Titel, ein Publikationsdatum (`YYYY-MM-DD`) und
   `<div type="news" subtype="published">`. Ein Bild liegt unter `images/` und
   wird in der TEI-Datei mit seinem Dateinamen verknüpft.
2. Für die Startseite den Eintrag `<term type="homepage">yes</term>` unter
   `<keywords scheme="#bebb-news">` setzen. Sonst erscheint die Meldung nur
   im News-Archiv.
3. Nach dem Push auf GitHub unter **Actions → Publish approved BEBB news**
   auf **Run workflow** klicken und `main` wählen. Ein Push aktualisiert den
   Feed nicht automatisch. Der Workflow veröffentlicht nur den Export,
   nicht das ganze Repository.
4. Den [News-Feed](https://projectbebb.github.io/BEBB_News/feed.xml) prüfen.
   Sobald die BEBB-App an den Feed angebunden ist, ist für weitere Meldungen
   weder eine neue App-XAR noch ein Upload nach eXist nötig.

Lokaler Probelauf ohne Veröffentlichung:
`python3 scripts/export-news.py . /path/to/new-preview-dir`
