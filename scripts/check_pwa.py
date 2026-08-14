#!/usr/bin/env python3
"""Static PWA contract checks for the learning hub."""
from pathlib import Path
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[1]

def png_size(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', f'{path} is not PNG'
    return struct.unpack('>II', data[16:24])

def main():
    manifest_path = ROOT / 'manifest.webmanifest'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['name'] == '精萃領導™學習中心'
    assert manifest['short_name'] == '精萃領導'
    assert manifest['start_url'] == './index.html'
    assert manifest['scope'] == './'
    assert manifest['display'] == 'standalone'
    assert {icon['sizes'] for icon in manifest['icons']} >= {'192x192', '512x512'}
    for size in (192, 512):
        assert png_size(ROOT / f'assets/icon-{size}.png') == (size, size)
    assert png_size(ROOT / 'assets/apple-touch-icon.png') == (180, 180)

    sw = (ROOT / 'service-worker.js').read_text()
    for marker in ('/api/', '/.netlify/functions/', '/audio_summaries/', 'request.method !==', 'url.origin !== self.location.origin'):
        assert marker in sw, f'missing service worker safety rule: {marker}'

    for page in [ROOT / 'index.html', *sorted(ROOT.glob('Article_Learning_Article*.html'))]:
        html = page.read_text()
        assert 'rel="manifest"' in html, f'missing manifest link: {page.name}'
        assert 'apple-mobile-web-app-capable' in html, f'missing iOS metadata: {page.name}'
        assert 'pwa.js' in html, f'missing install controller: {page.name}'
    pwa = (ROOT / 'pwa.js').read_text()
    assert 'beforeinstallprompt' in pwa and 'appinstalled' in pwa
    assert 'Safari 點分享' in pwa
    print('PWA checks: OK')

if __name__ == '__main__':
    main()
