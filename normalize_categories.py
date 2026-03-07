#!/usr/bin/env python3
"""Normalize and merge similar M3U categories."""

import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Mapping of original categories to normalized categories
CATEGORY_MAP = {
    # Entertainment / Entretenimiento
    "Entretenimiento": "Entretenimiento",
    "ENTRETENIMIENTO": "Entretenimiento",
    "Entertainment": "Entretenimiento",
    "Entertainment;Music": "Entretenimiento",
    "Entertainment;Travel": "Entretenimiento",
    "Entertainment;Lifestyle;Music": "Entretenimiento",
    "Entertainment;Family": "Entretenimiento",
    "Entertainment;Family;General;News": "Entretenimiento",
    "Entertainment;News": "Entretenimiento",
    "Entertainment;Music;News": "Entretenimiento",
    "Entertainment;Sports": "Entretenimiento",
    "Culture;Entertainment": "Entretenimiento",
    "Auto;Entertainment": "Entretenimiento",
    "Comedy;Entertainment": "Entretenimiento",
    "Culture;Education;Entertainment": "Entretenimiento",

    # TV Premium
    "TV PREMIUM": "TV Premium",
    "TV PREMIUM 2": "TV Premium",

    # Movies / Cine / Películas
    "CINE": "Cine y Películas",
    "CINE Y SERIES": "Cine y Películas",
    "Movies": "Cine y Películas",
    "ENGLISH MOVIES": "Cine y Películas",
    "PELICULAS": "Cine y Películas",
    "Películas": "Cine y Películas",
    "Movies;Series": "Cine y Películas",
    "Family;Movies": "Cine y Películas",
    "Classic;Movies": "Cine y Películas",
    "Movies;Music": "Cine y Películas",
    "Movies;News": "Cine y Películas",
    "Kids;Movies": "Cine y Películas",
    "Culture;Documentary;Entertainment;General;Movies;Music": "Cine y Películas",
    "VOD A LA CARTA": "Cine y Películas",

    # Series
    "Series": "Series",
    "NOVELAS": "Series",
    "Novelas": "Series",
    "Classic;Series": "Series",
    "General;Series": "Series",
    "Auto;Series": "Series",
    "Kids;Series": "Series",

    # Sports / Deportes
    "Deportes": "Deportes",
    "DEPORTES": "Deportes",
    "Sports": "Deportes",
    "News;Sports": "Deportes",
    "DEPORTES MUNDIAL": "Deportes",
    "DEPORTES PPV (NBA,NFL,MLB)": "Deportes",
    "EVENTOS PPV": "Deportes",
    "Competencia": "Deportes",

    # News / Noticias
    "News": "Noticias",
    "Noticias": "Noticias",
    "NOTICIAS": "Noticias",
    "General;News": "Noticias",
    "Business;News": "Noticias",
    "Culture;News": "Noticias",
    "Music;News": "Noticias",
    "Documentary;News": "Noticias",
    "Education;News": "Noticias",
    "Legislative;News": "Noticias",

    # Music / Música
    "Music": "Música",
    "MUSICA": "Música",
    "Musica": "Música",
    "Música": "Música",
    "Classic;Music": "Música",
    "Music;Religious": "Música",
    "Music;News;Religious": "Música",

    # Kids / Infantil
    "Kids": "Infantil",
    "INFANTIL": "Infantil",
    "Animation;Kids": "Infantil",
    "Kids;Religious": "Infantil",
    "Education;Kids": "Infantil",
    "Kids;Lifestyle": "Infantil",
    "Animation;Kids;Religious": "Infantil",
    "Teen": "Infantil",

    # Documentary / Documental
    "Documentary": "Documentales",
    "DOCUMENTAL": "Documentales",
    "Documentary;Science": "Documentales",
    "Documentary;Education": "Documentales",
    "Culture;Documentary": "Documentales",
    "Documentary;Entertainment": "Documentales",

    # Religion
    "Religious": "Religión",
    "RELIGION": "Religión",
    "Culture;Religious": "Religión",
    "General;Religious": "Religión",
    "Family;Religious": "Religión",

    # Comedy
    "Comedy": "Comedia",
    "Comedia": "Comedia",
    "COMEDIA": "Comedia",

    # Animation / Anime
    "Animation": "Anime y Animación",
    "Anime & Gaming": "Anime y Animación",

    # 24/7
    "24/7": "Canales 24/7",
    "CANALES 24/7": "Canales 24/7",
    "24/7 U.S.A": "Canales 24/7",

    # Pluto TV
    "PLUTO TV": "Pluto TV",
    "Pluto TV": "Pluto TV",
    "DISTRO TV": "Pluto TV / Gratis",

    # Education / Educación
    "Education": "Educación",
    "EDUCACION": "Educación",
    "Culture;Education": "Educación",
    "Education;Lifestyle;Science": "Educación",
    "Culture;Education;Lifestyle": "Educación",
    "Science": "Educación",

    # Culture
    "Culture": "Cultura",
    "CULTURAL": "Cultura",
    "Culture;Family": "Cultura",

    # Lifestyle
    "Lifestyle": "Estilo de Vida",
    "Estilo de Vida": "Estilo de Vida",
    "Lifestyle;Relax": "Estilo de Vida",
    "Relax": "Estilo de Vida",
    "Lifestyle;Shop": "Estilo de Vida",

    # Cooking
    "Cooking": "Cocina",
    "Cooking;Shop": "Cocina",

    # Travel
    "Travel": "Viajes",
    "Auto;Travel": "Viajes",

    # Outdoor
    "Outdoor": "Naturaleza",

    # Business
    "Business": "Negocios",
    "Business;Culture;Lifestyle": "Negocios",

    # Shop
    "Shop": "Shopping",

    # Auto
    "Auto": "Autos",

    # Classic / Retro
    "Classic": "Clásicos / Retro",
    "Retro": "Clásicos / Retro",

    # Legislative
    "Legislative": "Gobierno / Legislativo",

    # Weather
    "Weather": "Clima",

    # Family
    "Family": "Familiar",
    "Family;General": "Familiar",

    # Reality
    "Reality": "Reality",

    # General
    "General": "General",
    "International": "General",
    "INTERNACIONAL": "General",

    # Investigación / Curiosidad
    "Investigación": "Curiosidades",
    "Curiosidad": "Curiosidades",

    # South Park (special)
    "South Park": "South Park",

    # Radio
    "Radio": "Radio",

    # INFO
    "INFO": "Info / Otros",
    "Nacional": "Info / Otros",
    "Undefined": "Info / Otros",
    "": "Info / Otros",
    "Sin Categoría": "Sin Categoría",

    # XXX
    "XXX": "Adultos (XXX)",

    # === COUNTRIES ===
    "ARGENTINA": "Argentina",
    "Argentina": "Argentina",

    "CHILE": "Chile",
    "Chile": "Chile",

    "COLOMBIA": "Colombia",
    "Colombia": "Colombia",

    "MÉXICO": "México",
    "MEXICO": "México",
    "Mexico": "México",

    "ESPAÑA": "España",
    "ESPANA": "España",

    "PERÚ": "Perú",
    "PERU": "Perú",

    "ECUADOR": "Ecuador",
    "Ecuador": "Ecuador",

    "VENEZUELA": "Venezuela",

    "URUGUAY": "Uruguay",

    "BOLIVIA": "Bolivia",

    "PARAGUAY": "Paraguay",

    "PANAMA": "Panamá",
    "HONDURAS": "Honduras",
    "COSTA RICA": "Costa Rica",
    "Costa Rica": "Costa Rica",
    "EL SALVADOR": "El Salvador",
    "GUATEMALA": "Guatemala",
    "NICARAGUA": "Nicaragua",
    "PUERTO RICO": "Puerto Rico",
    "Puerto Rico": "Puerto Rico",
    "REPUBLICA DOMINICANA": "Rep. Dominicana",
    "REP DOMINICANA": "Rep. Dominicana",
    "CUBA": "Cuba",
    "Haiti": "Haití",

    "USA": "Estados Unidos",
    "CANADA": "Canadá",
    "Canada": "Canadá",
    "UK": "Reino Unido",
    "United Kingdom": "Reino Unido",
    "REINO UNIDO": "Reino Unido",

    "BRASIL": "Brasil",
    "Brazil": "Brasil",

    "ITALIA": "Italia",
    "Italy": "Italia",

    "Russia": "Rusia",
    "RUSIA": "Rusia",
    "RUSSIA": "Rusia",

    "France": "Francia",
    "FRANCIA": "Francia",

    "Germany": "Alemania",
    "ALEMANIA": "Alemania",

    "PORTUGAL": "Portugal",

    "Greece": "Grecia",
    "GRECIA": "Grecia",

    "Ukraine": "Ucrania",
    "UKRAINE": "Ucrania",
    "UCRANIA": "Ucrania",

    "India": "India",
    "INDIA": "India",

    "China": "China",
    "Taiwan": "China / Taiwan",

    "Australia": "Australia",
    "New Zealand": "Australia / NZ",

    "Netherlands": "Países Bajos",
    "PAISES BAJOS": "Países Bajos",

    "Ireland": "Irlanda",
    "Belgium": "Bélgica",
    "Switzerland": "Suiza",
    "Austria": "Austria",
    "Poland": "Polonia",
    "Czechia": "Rep. Checa",
    "Slovakia": "Eslovaquia",
    "Hungary": "Hungría",
    "Romania": "Rumanía",
    "ROMANIA": "Rumanía",
    "Bulgaria": "Bulgaria",
    "BULGARIA": "Bulgaria",
    "Serbia": "Serbia",
    "Slovenia": "Eslovenia",
    "ESLOVENIA": "Eslovenia",
    "Bosnia": "Bosnia",
    "Albania": "Albania",
    "Latvia": "Letonia",
    "LATVIA": "Letonia",
    "Georgia": "Georgia",
    "Kazakhstan": "Kazajistán",
    "Turkmenistan": "Turkmenistán",
    "Azerbaijan": "Azerbaiyán",
    "Moldova": "Moldavia",
    "Norway": "Noruega",
    "SUECIA": "Suecia",

    "Turkey": "Turquía",
    "Iran": "Irán",
    "IRAN": "Irán",
    "Iraq": "Irak",
    "IRAQ": "Irak",
    "Lebanon": "Líbano",
    "Palestine": "Palestina",
    "Saudi Arabia": "Arabia Saudita",
    "ARABIA": "Arabia Saudita",
    "Israel": "Israel",
    "Egypt": "Egipto",
    "Yemen": "Yemen",

    "South Korea": "Corea del Sur",
    "JAPAN": "Japón",
    "INDONESIA": "Indonesia",
    "Vietnam": "Vietnam",
    "Thailand": "Tailandia",
    "Pakistan": "Pakistán",

    "Afghanistan": "Afganistán",
    "Algeria": "Argelia",
    "Cameroon": "Camerún",
    "Cyprus": "Chipre",
    "Curaçao": "Curazao",
    "Ghana": "Ghana",
}


def main():
    with open("m3u_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    groups = data["groups"]
    normalized = defaultdict(list)
    unmapped = []

    for orig_cat, channels in groups.items():
        norm_cat = CATEGORY_MAP.get(orig_cat)
        if norm_cat is None:
            unmapped.append(orig_cat)
            norm_cat = orig_cat  # Keep original if not mapped
        normalized[norm_cat].extend(channels)

    # Deduplicate by URL within each group
    for cat in normalized:
        seen = set()
        unique = []
        for ch in normalized[cat]:
            if ch['url'] not in seen:
                seen.add(ch['url'])
                unique.append(ch)
        normalized[cat] = unique

    # Sort by channel count
    sorted_cats = sorted(normalized.items(), key=lambda x: len(x[1]), reverse=True)

    # Separate into main groups
    content_cats = []
    country_cats = []
    country_names = {
        "Argentina", "Chile", "Colombia", "México", "España", "Perú", "Ecuador",
        "Venezuela", "Uruguay", "Bolivia", "Paraguay", "Panamá", "Honduras",
        "Costa Rica", "El Salvador", "Guatemala", "Nicaragua", "Puerto Rico",
        "Rep. Dominicana", "Cuba", "Haití", "Estados Unidos", "Canadá",
        "Reino Unido", "Brasil", "Italia", "Rusia", "Francia", "Alemania",
        "Portugal", "Grecia", "Ucrania", "India", "China", "China / Taiwan",
        "Australia", "Australia / NZ", "Países Bajos", "Irlanda", "Bélgica",
        "Suiza", "Austria", "Polonia", "Rep. Checa", "Eslovaquia", "Hungría",
        "Rumanía", "Bulgaria", "Serbia", "Eslovenia", "Bosnia", "Albania",
        "Letonia", "Georgia", "Kazajistán", "Turkmenistán", "Azerbaiyán",
        "Moldavia", "Noruega", "Suecia", "Turquía", "Irán", "Irak", "Líbano",
        "Palestina", "Arabia Saudita", "Israel", "Egipto", "Yemen",
        "Corea del Sur", "Japón", "Indonesia", "Vietnam", "Tailandia",
        "Pakistán", "Afganistán", "Argelia", "Camerún", "Chipre", "Curazao",
        "Ghana",
    }

    for cat, chs in sorted_cats:
        if cat in country_names:
            country_cats.append((cat, chs))
        else:
            content_cats.append((cat, chs))

    total = sum(len(chs) for _, chs in sorted_cats)
    print(f"TOTAL CANALES ÚNICOS (después de deduplicar): {total}")
    print()

    # Print content categories
    print("=" * 70)
    print("CATEGORÍAS DE CONTENIDO")
    print("=" * 70)
    for i, (cat, chs) in enumerate(content_cats, 1):
        print(f"\n[{i}] {cat} ({len(chs)} canales)")
        print("-" * 50)
        # Show sample channels
        for ch in chs[:8]:
            print(f"    - {ch['name']}")
        if len(chs) > 8:
            print(f"    ... y {len(chs) - 8} más")

    # Print country categories
    print("\n" + "=" * 70)
    print("CATEGORÍAS POR PAÍS")
    print("=" * 70)
    country_cats_sorted = sorted(country_cats, key=lambda x: len(x[1]), reverse=True)
    for i, (cat, chs) in enumerate(country_cats_sorted, 1):
        print(f"  [{i}] {cat} ({len(chs)} canales)")

    if unmapped:
        print(f"\n[!] Categorías no mapeadas: {unmapped}")

    # Save normalized data
    output = {
        "content_categories": {cat: chs for cat, chs in content_cats},
        "country_categories": {cat: chs for cat, chs in country_cats_sorted},
        "total_channels": total,
    }
    with open("m3u_normalized.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDatos normalizados guardados en m3u_normalized.json")


if __name__ == "__main__":
    main()
