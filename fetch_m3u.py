#!/usr/bin/env python3
"""Download and parse M3U playlists, group channels by category."""

import requests
import re
import json
import sys
import os
from collections import defaultdict
from urllib.parse import urlparse

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

URLS = [
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
    "https://pastebin.com/raw/wCnH-1-dseportes-CDX2",
    "https://pastebin.com/raw/sfym-nbrda-2SDK",
    "https://pastebin.com/raw/K-futbsol11VtaQaMC",
    "http://bit.ly/futbolonlined33-applil",
    "http://bit.ly/deportesgeneral33-sapplil",
    "http://bit.ly/DeportesYmasdsyaj12",
    "http://bit.ly/tvypeadusdfltosiptv",
    "http://bit.ly/18masadusltos33",
    "http://bit.ly/PelisAdultaos331n",
    "http://bit.ly/AdultosIdPTVnn32",
    "http://bit.ly/PELISSM3U",
    "http://bit.ly/Pelis-IPTv",
    "http://bit.ly/TVFilms",
    "http://bit.ly/tvypelism3u",
    "http://bit.ly/Pelis-IsdfPT331",
    "http://bit.ly/TV14f6Films",
    "http://bit.ly/tvy632speli222sm3u",
    "http://bit.ly/PELISdsS11245iptv",
    "http://bit.ly/PelisHDgdgs33Alterna",
    "http://bit.ly/TV12467fFilms",
    "http://bit.ly/Peli5663f2IPTv",
    "http://bit.ly/tvysseries331",
    "http://bit.ly/Serie35f677FULL",
    "http://bit.ly/Series55g52FULL",
    "http://bit.ly/series13v4flixx",
]

def parse_m3u(content, source_url):
    """Parse M3U content and extract channels."""
    channels = []
    lines = content.strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            # Extract metadata
            extinf = line

            # Extract group-title
            group_match = re.search(r'group-title="([^"]*)"', extinf)
            group = group_match.group(1) if group_match else "Sin Categoría"

            # Extract channel name (after the last comma)
            name_match = re.search(r',(.+)$', extinf)
            name = name_match.group(1).strip() if name_match else "Unknown"

            # Extract logo
            logo_match = re.search(r'tvg-logo="([^"]*)"', extinf)
            logo = logo_match.group(1) if logo_match else ""

            # Extract tvg-id
            tvgid_match = re.search(r'tvg-id="([^"]*)"', extinf)
            tvg_id = tvgid_match.group(1) if tvgid_match else ""

            # Next non-empty, non-comment line is the URL
            i += 1
            stream_url = ""
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line and not next_line.startswith('#'):
                    stream_url = next_line
                    break
                elif next_line.startswith('#EXTINF:'):
                    i -= 1  # Back up so outer loop picks it up
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
                    'extinf': extinf,
                })
        i += 1

    return channels

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

def main():
    all_channels = []
    results = {"success": [], "failed": []}

    for url in URLS:
        print(f"Fetching: {url} ... ", end="", flush=True)
        content = fetch_url(url)
        if content and ('#EXTINF' in content or '#EXTM3U' in content):
            channels = parse_m3u(content, url)
            all_channels.extend(channels)
            results["success"].append({"url": url, "channels": len(channels)})
            print(f"OK ({len(channels)} canales)")
        elif content:
            # Maybe it's a plain list of URLs
            lines = [l.strip() for l in content.split('\n') if l.strip() and l.strip().startswith('http')]
            if lines:
                for stream_url in lines:
                    all_channels.append({
                        'name': stream_url.split('/')[-1],
                        'group': 'Sin Categoría',
                        'url': stream_url,
                        'logo': '',
                        'tvg_id': '',
                        'source': url,
                        'extinf': '',
                    })
                results["success"].append({"url": url, "channels": len(lines)})
                print(f"OK ({len(lines)} URLs planas)")
            else:
                results["failed"].append({"url": url, "reason": "No M3U content found"})
                print("SKIP (no M3U content)")
        else:
            results["failed"].append({"url": url, "reason": "Failed to download"})
            print("FAILED")

    # Group by category
    groups = defaultdict(list)
    for ch in all_channels:
        groups[ch['group']].append(ch)

    # Remove exact duplicate URLs within each group
    for group_name in groups:
        seen_urls = set()
        unique = []
        for ch in groups[group_name]:
            if ch['url'] not in seen_urls:
                seen_urls.add(ch['url'])
                unique.append(ch)
        groups[group_name] = unique

    # Print summary
    print("\n" + "="*70)
    print(f"RESUMEN DE DESCARGA")
    print("="*70)
    print(f"URLs exitosas: {len(results['success'])}")
    print(f"URLs fallidas: {len(results['failed'])}")
    print(f"Total canales encontrados: {sum(len(v) for v in groups.values())}")
    print(f"Total categorías: {len(groups)}")

    if results['failed']:
        print(f"\nURLs que fallaron:")
        for f in results['failed']:
            print(f"  - {f['url']}: {f['reason']}")

    print("\n" + "="*70)
    print("CATEGORÍAS ENCONTRADAS")
    print("="*70)

    # Sort groups by number of channels (descending)
    sorted_groups = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)

    for idx, (group_name, channels) in enumerate(sorted_groups, 1):
        print(f"\n[{idx}] {group_name} ({len(channels)} canales)")
        print("-" * 50)
        for ch in channels[:10]:  # Show first 10
            print(f"    - {ch['name']}")
        if len(channels) > 10:
            print(f"    ... y {len(channels) - 10} más")

    # Save full data to JSON for later processing
    output = {
        "results": results,
        "groups": {k: v for k, v in sorted_groups},
        "total_channels": sum(len(v) for v in groups.values()),
        "total_groups": len(groups),
    }

    with open("m3u_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDatos guardados en m3u_data.json")

if __name__ == "__main__":
    main()
