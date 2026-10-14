BD STUROVA - ORIENTACNE OSADENIE SITUACIE

Vsetky rastry a GeoJSON su v EPSG:8353.
V QGIS nacitat 00_Ortofoto_ZBGIS.tif, 01_DMR6.tif, 02_Situacia_orientacne.tif (navrchu). GeoJSON je doplnkova vektorova kresba.
Vybrana prva kopia situacie z DWG, bez druhej posunutej kopie a bez razitka. Raster obsahuje ciary, obluky, kruznice, polylinie a hlavne texty; nie vsetky srafy a blokove symboly. Povodny DWG ostava autoritativny.
Transformacia: jednotky delene 1000, potom rigidny posun a rotacia; mierka nebola prisposobovana.
8 manualne priradenych rohov na 2 budovach; cielove body odcitane z WMS ZBGIS vrstvy 49 Budova v EPSG:8353, raster 1/6 m. RMSE=1.27 m na pouzitych bodoch; nejde o nezavislu presnost. Maximalna odchylka na pouzitych bodoch 2.03 m. Geometrie referencnych budov mozu byt generalizovane.
Nepouzivat na vytycovanie, realizaciu ani presny vypocet zemnych prac. Na to je potrebne geodeticke overenie.
Vyskovy system DMR nie je potvrdeny. Z=263.650 pre projektovu nulu nebolo pouzite na upravu terenu.
ZBGIS WMS: https://zbgisws.skgeodesy.sk/zbgis_wms_featureinfo/service.svc/get
Ortofoto WMS: https://zbgisws.skgeodesy.sk/zbgis_ortofoto_wms/service.svc/get
Referencne data nacitane 2026-10-14.

Projekt BD_STUROVA.qgs ma prednastavene vrstvy (situacia nad ortofotom, DMR je nacitany a vypnuty). Projekt bol overeny ako XML, otvorenie v QGIS nebolo v tomto prostredi otestovane.
