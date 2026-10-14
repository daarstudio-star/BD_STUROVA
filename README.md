# BD Štúrova – projektové vrstvy

Otvorte `index.html`. Ľavý panel obsahuje ZÁKLADY · 65 % a prepnutie späť na terén, vrstevnice a situáciu. Otáčanie a priblíženie sú dostupné v oboch pohľadoch. Pre úplnú funkciu ovládania vnoreného pohľadu spustite v tomto adresári `python -m http.server 8000` a otvorte http://localhost:8000.

## Obsah
- `vystupy/`: všetky doteraz dostupné finálne výstupy, obrázky, profily, geologická interpretácia, HTML prehliadače, GIS vrstvy a archívy v01/v02.
- `vystupy/BD_STUROVA_vrstvy/`: DMR 6.0, ortofoto, situácia, kontrolné body, transformácia a QGIS projekt.
- `vystupy/BD_STUROVA_zaklady_v02/`: aktuálne základové prvky GLB/OBJ, geometria a atribúty JSON/CSV, generátor, zoznam otvorených detailov.
- `podklady/`: dostupné pôvodné DWG pôdorysov a rezov, PDF pôdorysov, všetkých šiestich rezov a pohľadov.
- `vrstva_zakladov.json`: názov vrstvy, pracovná dôvera a osem otvorených otázok.
- `manifest.json`: zoznam súborov a kontrolné súčty SHA-256.

## Stav
VRSTVA ZÁKLADOV v0.2: pracovná dôvera 65 %, orientačný odhad, nie štatistická presnosť. 110 objemových prvkov. 11 nedoriešených oblastí a P31/P41 bez jednoznačných výšok. Nie je to dokončený IFC BIM model. Geometria zostáva nezmenená.

Základy sú v lokálnych CAD súradniciach, ±0,000 = 263,650 m. Nie sú zlúčené s DMR do spoločnej scény: ich georeferencovanie ešte nie je overené. Situácia na teréne má orientačné osadenie s RMSE 1,27 m; výškový systém DMR nie je potvrdený. Geologický obrázok je interpretácia, nie výsledok IGP.

Zdrojový projekt: https://drive.google.com/drive/folders/1h1nt2uwKaRwJnOPqug7kXpLQropPfxNh
PDF dokumentácia: https://drive.google.com/drive/folders/17O5_RcX8CYjAMJJFUV-a9_uU0jLPq2kv

GitHub: https://github.com/daarstudio-star/BD_STUROVA

Aktuálny index.html je samostatný prehliadač s červenými, oranžovými a zelenými poznámkami, filtrovaním podľa dôležitosti a pevnou projektovou nulou. Základy sa stále zobrazujú v samostatnom lokálnom pohľade. Spoločná georeferencovaná scéna všetkých vrstiev ešte NIE JE dokončená.

Dokumentácia potvrdzuje 100 mm podkladného betónu a minimálne 100 mm štrku pod ŽB základmi. Odvodené minimálne úrovne dna výkopu sú 258,450 / 258,050 / 257,650 m, pri potrebe výmeny zeminy nižšie. Technická správa uvádza existenciu IGP; samotná správa IGP zatiaľ nebola overená. Presný rozpočet zemných prác nie je hotový.
