#!/usr/bin/env python3
"""
M3U Playlist Unifier
====================
Script automatizado para:
1. Descargar múltiples listas M3U desde URLs
2. Parsear y extraer canales con sus categorías
3. Normalizar y agrupar categorías similares
4. Deduplicar canales por URL
5. Permitir al usuario seleccionar categorías
6. Generar una lista M3U unificada
7. Testear una muestra de canales

Uso:
    python m3u_unifier.py                    # Modo interactivo
    python m3u_unifier.py --urls urls.txt    # Cargar URLs desde archivo
    python m3u_unifier.py --config config.json  # Usar configuración previa
"""

import requests
import re
import json
import sys
import os
import random
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ============================================================
# DEFAULT URLS - Edit this list to add/remove sources
# ============================================================
DEFAULT_URLS = [
    "http://tecnotv.club/0503M/lista.m3u",
    "http://tecnotv.club/0503M/lista1.m3u",
    "http://tecnotv.club/0503M/lista2.m3u",
    "http://tecnotv.club/0503M/lista3.m3u",
    "http://tecnotv.club/0503M/lista4.m3u",
    "http://tecnotv.club/0503M/lista5.m3u",
    "http://tecnotv.club/0503M/geomex.m3u",
    "http://tecnotv.club/0503M/android.m3u",
    "http://tecnotv.club/0503M/android1.m3u",
    "http://tecnotv.club/0503M/android2.m3u",
    "http://tecnotv.club/0503M/android3.m3u",
    "http://tecnotv.club/0503M/android4.m3u",
    "http://www.m3u.cl/playlist/AR.m3u",
    "https://iptv-org.github.io/iptv/countries/ar.m3u",
    "https://pastebin.com/raw/AAk7Ck69",
    "https://pastebin.com/raw/J2Eb9xQg",
    "http://bit.ly/tvypelism3u",
]

# ============================================================
# CATEGORY NORMALIZATION MAP
# ============================================================
CATEGORY_MAP = {
    # Entretenimiento
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

    # Cine y Películas
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

    # Deportes
    "Deportes": "Deportes",
    "DEPORTES": "Deportes",
    "Sports": "Deportes",
    "News;Sports": "Deportes",
    "DEPORTES MUNDIAL": "Deportes",
    "DEPORTES PPV (NBA,NFL,MLB)": "Deportes",
    "EVENTOS PPV": "Deportes",
    "Competencia": "Deportes",

    # Noticias
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

    # Música
    "Music": "Música",
    "MUSICA": "Música",
    "Musica": "Música",
    "Música": "Música",
    "Classic;Music": "Música",
    "Music;Religious": "Música",
    "Music;News;Religious": "Música",

    # Infantil
    "Kids": "Infantil",
    "INFANTIL": "Infantil",
    "Animation;Kids": "Infantil",
    "Kids;Religious": "Infantil",
    "Education;Kids": "Infantil",
    "Kids;Lifestyle": "Infantil",
    "Animation;Kids;Religious": "Infantil",
    "Teen": "Infantil",

    # Documentales
    "Documentary": "Documentales",
    "DOCUMENTAL": "Documentales",
    "Documentary;Science": "Documentales",
    "Documentary;Education": "Documentales",
    "Culture;Documentary": "Documentales",
    "Documentary;Entertainment": "Documentales",

    # Religión
    "Religious": "Religión",
    "RELIGION": "Religión",
    "Culture;Religious": "Religión",
    "General;Religious": "Religión",
    "Family;Religious": "Religión",

    # Comedia
    "Comedy": "Comedia",
    "Comedia": "Comedia",
    "COMEDIA": "Comedia",

    # Anime y Animación
    "Animation": "Anime y Animación",
    "Anime & Gaming": "Anime y Animación",

    # Canales 24/7
    "24/7": "Canales 24/7",
    "CANALES 24/7": "Canales 24/7",
    "24/7 U.S.A": "Canales 24/7",

    # Pluto TV
    "PLUTO TV": "Pluto TV",
    "Pluto TV": "Pluto TV",
    "DISTRO TV": "Pluto TV / Gratis",

    # Educación
    "Education": "Educación",
    "EDUCACION": "Educación",
    "Culture;Education": "Educación",
    "Education;Lifestyle;Science": "Educación",
    "Culture;Education;Lifestyle": "Educación",
    "Science": "Educación",

    # Cultura
    "Culture": "Cultura",
    "CULTURAL": "Cultura",
    "Culture;Family": "Cultura",

    # Estilo de Vida
    "Lifestyle": "Estilo de Vida",
    "Estilo de Vida": "Estilo de Vida",
    "Lifestyle;Relax": "Estilo de Vida",
    "Relax": "Estilo de Vida",
    "Lifestyle;Shop": "Estilo de Vida",

    # Cocina
    "Cooking": "Cocina",
    "Cooking;Shop": "Cocina",

    # Viajes
    "Travel": "Viajes",
    "Auto;Travel": "Viajes",

    # Naturaleza
    "Outdoor": "Naturaleza",

    # Negocios
    "Business": "Negocios",
    "Business;Culture;Lifestyle": "Negocios",

    # Shopping
    "Shop": "Shopping",

    # Autos
    "Auto": "Autos",

    # Clásicos / Retro
    "Classic": "Clásicos / Retro",
    "Retro": "Clásicos / Retro",

    # Gobierno
    "Legislative": "Gobierno / Legislativo",

    # Clima
    "Weather": "Clima",

    # Familiar
    "Family": "Familiar",
    "Family;General": "Familiar",

    # Reality
    "Reality": "Reality",

    # General
    "General": "General",
    "International": "General",
    "INTERNACIONAL": "General",

    # Curiosidades
    "Investigación": "Curiosidades",
    "Curiosidad": "Curiosidades",

    # South Park
    "South Park": "South Park",

    # Radio
    "Radio": "Radio",

    # Info / Otros
    "INFO": "Info / Otros",
    "Nacional": "Info / Otros",
    "Undefined": "Info / Otros",
    "": "Info / Otros",
    "Sin Categoría": "Sin Categoría",

    # Adultos
    "XXX": "Adultos (XXX)",

    # === PAÍSES ===
    "ARGENTINA": "Argentina", "Argentina": "Argentina",
    "CHILE": "Chile", "Chile": "Chile",
    "COLOMBIA": "Colombia", "Colombia": "Colombia",
    "MÉXICO": "México", "MEXICO": "México", "Mexico": "México",
    "ESPAÑA": "España", "ESPANA": "España",
    "PERÚ": "Perú", "PERU": "Perú",
    "ECUADOR": "Ecuador", "Ecuador": "Ecuador",
    "VENEZUELA": "Venezuela",
    "URUGUAY": "Uruguay",
    "BOLIVIA": "Bolivia",
    "PARAGUAY": "Paraguay",
    "PANAMA": "Panamá",
    "HONDURAS": "Honduras",
    "COSTA RICA": "Costa Rica", "Costa Rica": "Costa Rica",
    "EL SALVADOR": "El Salvador",
    "GUATEMALA": "Guatemala",
    "NICARAGUA": "Nicaragua",
    "PUERTO RICO": "Puerto Rico", "Puerto Rico": "Puerto Rico",
    "REPUBLICA DOMINICANA": "Rep. Dominicana", "REP DOMINICANA": "Rep. Dominicana",
    "CUBA": "Cuba", "Haiti": "Haití",
    "USA": "Estados Unidos",
    "CANADA": "Canadá", "Canada": "Canadá",
    "UK": "Reino Unido", "United Kingdom": "Reino Unido", "REINO UNIDO": "Reino Unido",
    "BRASIL": "Brasil", "Brazil": "Brasil",
    "ITALIA": "Italia", "Italy": "Italia",
    "Russia": "Rusia", "RUSIA": "Rusia", "RUSSIA": "Rusia",
    "France": "Francia", "FRANCIA": "Francia",
    "Germany": "Alemania", "ALEMANIA": "Alemania",
    "PORTUGAL": "Portugal",
    "Greece": "Grecia", "GRECIA": "Grecia",
    "Ukraine": "Ucrania", "UKRAINE": "Ucrania", "UCRANIA": "Ucrania",
    "India": "India", "INDIA": "India",
    "China": "China", "Taiwan": "China / Taiwan",
    "Australia": "Australia", "New Zealand": "Australia / NZ",
    "Netherlands": "Países Bajos", "PAISES BAJOS": "Países Bajos",
    "Ireland": "Irlanda",
    "Belgium": "Bélgica", "Switzerland": "Suiza", "Austria": "Austria",
    "Poland": "Polonia", "Czechia": "Rep. Checa", "Slovakia": "Eslovaquia",
    "Hungary": "Hungría", "Romania": "Rumanía", "ROMANIA": "Rumanía",
    "Bulgaria": "Bulgaria", "BULGARIA": "Bulgaria",
    "Serbia": "Serbia", "Slovenia": "Eslovenia", "ESLOVENIA": "Eslovenia",
    "Bosnia": "Bosnia", "Albania": "Albania",
    "Latvia": "Letonia", "LATVIA": "Letonia",
    "Georgia": "Georgia", "Kazakhstan": "Kazajistán",
    "Turkmenistan": "Turkmenistán", "Azerbaijan": "Azerbaiyán",
    "Moldova": "Moldavia", "Norway": "Noruega", "SUECIA": "Suecia",
    "Turkey": "Turquía", "Iran": "Irán", "IRAN": "Irán",
    "Iraq": "Irak", "IRAQ": "Irak", "Lebanon": "Líbano",
    "Palestine": "Palestina", "Saudi Arabia": "Arabia Saudita", "ARABIA": "Arabia Saudita",
    "Israel": "Israel", "Egypt": "Egipto", "Yemen": "Yemen",
    "South Korea": "Corea del Sur", "JAPAN": "Japón", "INDONESIA": "Indonesia",
    "Vietnam": "Vietnam", "Thailand": "Tailandia", "Pakistan": "Pakistán",
    "Afghanistan": "Afganistán", "Algeria": "Argelia", "Cameroon": "Camerún",
    "Cyprus": "Chipre", "Curaçao": "Curazao", "Ghana": "Ghana",
}

COUNTRY_NAMES = {
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


# ============================================================
# CORE FUNCTIONS
# ============================================================

def fetch_url(url, timeout=15):
    """Fetch a URL with error handling."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        return None


def parse_m3u(content, source_url):
    """Parse M3U content and extract channels."""
    channels = []
    lines = content.strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf = line

            group_match = re.search(r'group-title="([^"]*)"', extinf)
            group = group_match.group(1) if group_match else "Sin Categoría"

            name_match = re.search(r',(.+)$', extinf)
            name = name_match.group(1).strip() if name_match else "Unknown"

            logo_match = re.search(r'tvg-logo="([^"]*)"', extinf)
            logo = logo_match.group(1) if logo_match else ""

            tvgid_match = re.search(r'tvg-id="([^"]*)"', extinf)
            tvg_id = tvgid_match.group(1) if tvgid_match else ""

            i += 1
            stream_url = ""
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line and not next_line.startswith('#'):
                    stream_url = next_line
                    break
                elif next_line.startswith('#EXTINF:'):
                    i -= 1
                    break
                i += 1

            if stream_url:
                channels.append({
                    'name': name,
                    'group': group,
                    'url': stream_url,
                    'logo': logo,
                    'tvg_id': tvg_id,
                    'source': source_url,
                })
        i += 1

    return channels


def fetch_all_playlists(urls, max_workers=5):
    """Fetch all M3U playlists in parallel."""
    all_channels = []
    results = {"success": [], "failed": []}

    def process_url(url):
        content = fetch_url(url)
        if content and ('#EXTINF' in content or '#EXTM3U' in content):
            channels = parse_m3u(content, url)
            return url, channels, None
        elif content:
            lines = [l.strip() for l in content.split('\n')
                     if l.strip() and l.strip().startswith('http')]
            if lines:
                channels = [{
                    'name': u.split('/')[-1], 'group': 'Sin Categoría',
                    'url': u, 'logo': '', 'tvg_id': '', 'source': url,
                } for u in lines]
                return url, channels, None
            return url, None, "No M3U content"
        return url, None, "Failed to download"

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_url, url): url for url in urls}
        for future in as_completed(futures):
            url, channels, error = future.result()
            if channels:
                all_channels.extend(channels)
                results["success"].append({"url": url, "channels": len(channels)})
                print(f"  OK  {url} ({len(channels)} canales)")
            else:
                results["failed"].append({"url": url, "reason": error})
                print(f"  FAIL {url}: {error}")

    return all_channels, results


def normalize_categories(all_channels):
    """Normalize and group channels by merged categories."""
    normalized = defaultdict(list)

    for ch in all_channels:
        norm_cat = CATEGORY_MAP.get(ch['group'], ch['group'])
        normalized[norm_cat].append(ch)

    # Deduplicate by URL within each group
    for cat in normalized:
        seen = set()
        unique = []
        for ch in normalized[cat]:
            if ch['url'] not in seen:
                seen.add(ch['url'])
                unique.append(ch)
        normalized[cat] = unique

    # Separate content and country categories
    content_cats = {}
    country_cats = {}
    for cat, chs in sorted(normalized.items(), key=lambda x: len(x[1]), reverse=True):
        if cat in COUNTRY_NAMES:
            country_cats[cat] = chs
        else:
            content_cats[cat] = chs

    return content_cats, country_cats


def display_categories(content_cats, country_cats):
    """Display available categories for user selection."""
    print("\n" + "=" * 60)
    print("CATEGORÍAS DE CONTENIDO")
    print("=" * 60)

    content_list = sorted(content_cats.items(), key=lambda x: len(x[1]), reverse=True)
    for i, (cat, chs) in enumerate(content_list, 1):
        print(f"  [{i:>2}] {cat:<35} {len(chs):>5} canales")

    print("\n" + "=" * 60)
    print("CATEGORÍAS POR PAÍS")
    print("=" * 60)

    country_list = sorted(country_cats.items(), key=lambda x: len(x[1]), reverse=True)
    for i, (cat, chs) in enumerate(country_list, 1):
        print(f"  [{i:>2}] {cat:<35} {len(chs):>5} canales")

    return content_list, country_list


def select_categories(content_list, country_list):
    """Interactive category selection."""
    print("\n" + "-" * 60)
    print("SELECCIÓN DE CATEGORÍAS")
    print("-" * 60)

    # Content categories
    print("\nCategorías de contenido:")
    print("  Ingresa los números separados por coma (ej: 1,2,3,5)")
    print("  'all' para todas, 'all-X,Y' para todas excepto X e Y")
    choice = input("  > ").strip()

    selected_content = []
    if choice.lower() == 'all':
        selected_content = [cat for cat, _ in content_list]
    elif choice.lower().startswith('all-'):
        exclude = set(int(x) for x in choice[4:].split(','))
        selected_content = [cat for i, (cat, _) in enumerate(content_list, 1) if i not in exclude]
    else:
        indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
        selected_content = [content_list[i-1][0] for i in indices if 1 <= i <= len(content_list)]

    # Country categories
    print("\nCategorías por país:")
    print("  Ingresa los números separados por coma, 'all', 'none', o 'all-X,Y'")
    choice = input("  > ").strip()

    selected_countries = []
    if choice.lower() == 'all':
        selected_countries = [cat for cat, _ in country_list]
    elif choice.lower() == 'none':
        selected_countries = []
    elif choice.lower().startswith('all-'):
        exclude = set(int(x) for x in choice[4:].split(','))
        selected_countries = [cat for i, (cat, _) in enumerate(country_list, 1) if i not in exclude]
    else:
        indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
        selected_countries = [country_list[i-1][0] for i in indices if 1 <= i <= len(country_list)]

    return selected_content, selected_countries


def generate_m3u(content_cats, country_cats, selected_content, selected_countries, output_path):
    """Generate unified M3U file."""
    lines = ["#EXTM3U"]
    total = 0
    stats = {}

    for cat_name in selected_content:
        if cat_name in content_cats:
            channels = content_cats[cat_name]
            stats[cat_name] = len(channels)
            for ch in channels:
                logo_attr = f' tvg-logo="{ch["logo"]}"' if ch.get("logo") else ""
                tvgid_attr = f' tvg-id="{ch["tvg_id"]}"' if ch.get("tvg_id") else ""
                extinf = f'#EXTINF:-1{tvgid_attr}{logo_attr} group-title="{cat_name}",{ch["name"]}'
                lines.append(extinf)
                lines.append(ch["url"])
                total += 1

    for cat_name in selected_countries:
        if cat_name in country_cats:
            channels = country_cats[cat_name]
            stats[cat_name] = len(channels)
            for ch in channels:
                logo_attr = f' tvg-logo="{ch["logo"]}"' if ch.get("logo") else ""
                tvgid_attr = f' tvg-id="{ch["tvg_id"]}"' if ch.get("tvg_id") else ""
                extinf = f'#EXTINF:-1{tvgid_attr}{logo_attr} group-title="{cat_name}",{ch["name"]}'
                lines.append(extinf)
                lines.append(ch["url"])
                total += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return total, stats


def test_channels(m3u_path, sample_size=30, timeout=8):
    """Test a sample of channels from the M3U file."""
    with open(m3u_path, "r", encoding="utf-8") as f:
        content = f.readlines()

    channels = []
    i = 0
    while i < len(content):
        line = content[i].strip()
        if line.startswith('#EXTINF:'):
            name_match = re.search(r',(.+)$', line)
            group_match = re.search(r'group-title="([^"]*)"', line)
            name = name_match.group(1) if name_match else "?"
            group = group_match.group(1) if group_match else "?"
            if i + 1 < len(content):
                url = content[i + 1].strip()
                channels.append((name, group, url))
                i += 1
        i += 1

    sample = random.sample(channels, min(sample_size, len(channels)))
    ok_count = 0

    print(f"\nTesteando {len(sample)} canales aleatorios...")
    print("-" * 60)

    def test_one(item):
        name, group, url = item
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            chunk = resp.raw.read(1024)
            resp.close()
            ok = resp.status_code == 200 and len(chunk) > 0
            return name, group, ok, resp.status_code
        except Exception as e:
            return name, group, False, str(e)[:30]

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_one, item) for item in sample]
        for future in as_completed(futures):
            name, group, ok, status = future.result()
            label = "OK" if ok else "FAIL"
            print(f"  [{label:>4}] [{group[:15]:<15}] {name[:40]}")
            if ok:
                ok_count += 1

    pct = ok_count * 100 // len(sample) if sample else 0
    print(f"\nResultado: {ok_count}/{len(sample)} funcionando ({pct}%)")
    return ok_count, len(sample)


def save_config(urls, selected_content, selected_countries, output_path, config_path="m3u_config.json"):
    """Save current configuration for future runs."""
    config = {
        "urls": urls,
        "selected_content": selected_content,
        "selected_countries": selected_countries,
        "output_path": output_path,
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"Configuración guardada en {config_path}")


def load_config(config_path):
    """Load configuration from file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="M3U Playlist Unifier")
    parser.add_argument("--urls", help="Archivo con URLs (una por línea)")
    parser.add_argument("--config", help="Archivo de configuración JSON")
    parser.add_argument("--output", default="lista_unificada.m3u", help="Archivo de salida")
    parser.add_argument("--test", action="store_true", help="Testear canales después de generar")
    parser.add_argument("--test-count", type=int, default=30, help="Canales a testear")
    args = parser.parse_args()

    print("=" * 60)
    print("  M3U PLAYLIST UNIFIER")
    print("=" * 60)

    # Determine URLs
    if args.config and os.path.exists(args.config):
        config = load_config(args.config)
        urls = config["urls"]
        print(f"\nCargando configuración de {args.config}")
    elif args.urls and os.path.exists(args.urls):
        with open(args.urls, "r") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    else:
        urls = DEFAULT_URLS

    print(f"\nDescargando {len(urls)} listas M3U...")
    print("-" * 60)

    # Step 1: Fetch all playlists
    all_channels, results = fetch_all_playlists(urls)
    print(f"\nTotal: {len(all_channels)} canales de {len(results['success'])} fuentes")

    if not all_channels:
        print("No se encontraron canales. Abortando.")
        sys.exit(1)

    # Step 2: Normalize categories
    content_cats, country_cats = normalize_categories(all_channels)
    total_unique = sum(len(v) for v in content_cats.values()) + sum(len(v) for v in country_cats.values())
    print(f"Canales únicos: {total_unique}")

    # Step 3: Select categories
    if args.config and os.path.exists(args.config):
        selected_content = config["selected_content"]
        selected_countries = config["selected_countries"]
        print(f"\nUsando categorías de configuración:")
        print(f"  Contenido: {', '.join(selected_content)}")
        print(f"  Países: {', '.join(selected_countries) or 'ninguno'}")
    else:
        content_list, country_list = display_categories(content_cats, country_cats)
        selected_content, selected_countries = select_categories(content_list, country_list)

    # Step 4: Generate M3U
    output_path = args.output
    print(f"\nGenerando {output_path}...")
    total, stats = generate_m3u(content_cats, country_cats, selected_content, selected_countries, output_path)

    print(f"\nLista generada: {output_path}")
    print(f"Total canales: {total}")
    print("\nPor categoría:")
    for cat, count in stats.items():
        print(f"  {cat}: {count}")

    # Save config for future use
    save_config(urls, selected_content, selected_countries, output_path)

    # Step 5: Test channels
    if args.test or (not args.config):
        do_test = True
        if not args.config:
            answer = input("\n¿Testear canales? (s/n): ").strip().lower()
            do_test = answer in ('s', 'si', 'sí', 'y', 'yes')
        if do_test:
            test_channels(output_path, sample_size=args.test_count)

    print(f"\n¡Listo! Tu lista unificada está en: {output_path}")
    print(f"Para re-generar con la misma configuración:")
    print(f"  python {os.path.basename(__file__)} --config m3u_config.json")


if __name__ == "__main__":
    main()
