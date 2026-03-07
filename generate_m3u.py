#!/usr/bin/env python3
"""Generate unified M3U file from normalized data with selected categories."""

import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SELECTED_CONTENT = [
    "Entretenimiento",
    "TV Premium",
    "Cine y Películas",
    "Canales 24/7",
    "Música",
    "Deportes",
    "Noticias",
    "Series",
    "Infantil",
    "Pluto TV",
    "Documentales",
    "Comedia",
    "Anime y Animación",
    "Reality",
    "Religión",
    "Adultos (XXX)",
]

SELECTED_COUNTRIES = [
    "Argentina",
]


def main():
    with open("m3u_normalized.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    content_cats = data["content_categories"]
    country_cats = data["country_categories"]

    # Collect selected channels
    output_lines = ["#EXTM3U"]
    total = 0
    stats = {}

    # Add content categories
    for cat_name in SELECTED_CONTENT:
        if cat_name in content_cats:
            channels = content_cats[cat_name]
            stats[cat_name] = len(channels)
            for ch in channels:
                # Rebuild EXTINF line with normalized group
                logo_attr = f' tvg-logo="{ch["logo"]}"' if ch.get("logo") else ""
                tvgid_attr = f' tvg-id="{ch["tvg_id"]}"' if ch.get("tvg_id") else ""
                extinf = f'#EXTINF:-1{tvgid_attr}{logo_attr} group-title="{cat_name}",{ch["name"]}'
                output_lines.append(extinf)
                output_lines.append(ch["url"])
                total += 1

    # Add country categories
    for cat_name in SELECTED_COUNTRIES:
        if cat_name in country_cats:
            channels = country_cats[cat_name]
            stats[cat_name] = len(channels)
            for ch in channels:
                logo_attr = f' tvg-logo="{ch["logo"]}"' if ch.get("logo") else ""
                tvgid_attr = f' tvg-id="{ch["tvg_id"]}"' if ch.get("tvg_id") else ""
                extinf = f'#EXTINF:-1{tvgid_attr}{logo_attr} group-title="{cat_name}",{ch["name"]}'
                output_lines.append(extinf)
                output_lines.append(ch["url"])
                total += 1

    # Write M3U file
    output_path = "lista_unificada.m3u"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")

    print(f"Lista unificada generada: {output_path}")
    print(f"Total canales: {total}")
    print()
    print("Canales por categoría:")
    for cat, count in stats.items():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
