#!/usr/bin/env python3
"""Test a sample of channels from the unified M3U to check if they work."""

import requests
import sys
import random
import re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def test_stream(url, timeout=8):
    """Test if a stream URL is accessible."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
        # Read just enough to confirm it's streaming
        chunk = resp.raw.read(1024)
        resp.close()
        if resp.status_code == 200 and len(chunk) > 0:
            return True, resp.status_code
        return False, resp.status_code
    except Exception as e:
        return False, str(e)


def main():
    with open("lista_unificada.m3u", "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Parse channels
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            name_match = re.search(r',(.+)$', line)
            group_match = re.search(r'group-title="([^"]*)"', line)
            name = name_match.group(1) if name_match else "?"
            group = group_match.group(1) if group_match else "?"
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                channels.append((name, group, url))
                i += 1
        i += 1

    print(f"Total canales en lista: {len(channels)}")

    # Pick samples from different categories
    by_group = {}
    for name, group, url in channels:
        by_group.setdefault(group, []).append((name, url))

    # Test 3 random channels per category (max 5 categories)
    test_groups = ["Entretenimiento", "TV Premium", "Deportes", "Argentina", "Cine y Películas",
                   "Noticias", "Infantil", "Música", "Canales 24/7", "Series"]

    total_tested = 0
    total_ok = 0

    for group in test_groups:
        if group not in by_group:
            continue
        sample = random.sample(by_group[group], min(3, len(by_group[group])))
        print(f"\n--- {group} ---")
        for name, url in sample:
            ok, status = test_stream(url)
            emoji = "OK" if ok else "FAIL"
            print(f"  [{emoji}] {name[:50]:<50} (status: {status})")
            total_tested += 1
            if ok:
                total_ok += 1

    print(f"\n{'='*60}")
    print(f"Resultado: {total_ok}/{total_tested} canales funcionando ({total_ok*100//total_tested}%)")


if __name__ == "__main__":
    main()
