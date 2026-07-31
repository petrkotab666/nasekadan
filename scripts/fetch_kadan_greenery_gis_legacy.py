#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import ssl
import time
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import requests
from matplotlib.patches import Patch
from pyproj import Geod
from requests.adapters import HTTPAdapter
from shapely.geometry import Point, shape
from urllib3.poolmanager import PoolManager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.github' / 'research' / 'greenery-kadan-2026'
IMAGES = OUT / 'images'
OUT.mkdir(parents=True, exist_ok=True)
IMAGES.mkdir(parents=True, exist_ok=True)

BASE = 'https://gis.mesto-kadan.cz/portal/arcgis/rest/services/verejny_portal/Verejny_portal/MapServer'

# Pouze pro veřejný, pouze čtecí městský ArcGIS se zastaralým TLS. Ověření certifikátu zůstává zapnuté.
class LegacyServerConnectAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = ssl.create_default_context()
        ctx.options |= getattr(ssl, 'OP_LEGACY_SERVER_CONNECT', 0x4)
        try:
            ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
        except ssl.SSLError:
            pass
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_context=ctx, **pool_kwargs)

session = requests.Session()
session.mount('https://gis.mesto-kadan.cz/', LegacyServerConnectAdapter(max_retries=3))
session.headers.update({'User-Agent': 'NaseKadanResearch/1.1 (+https://nasekadan.cz)', 'Accept-Language': 'cs,en;q=0.7'})

LOCALITIES = [
    'Sídliště A, Kadaň', 'Sídliště B, Kadaň', 'Sídliště C, Kadaň', 'Sídliště D, Kadaň',
    'Strážiště I, Kadaň', 'Strážiště II, Kadaň', 'Strážiště III, Kadaň',
    'Obránců míru, Kadaň', 'Smetanovy sady, Kadaň', 'Rooseveltovy sady, Kadaň',
    'Na Podlesí, Kadaň', 'Chomutovská, Kadaň', 'Husova, Kadaň', 'Golovinova, Kadaň',
    'Věžní, Kadaň', 'Jitřní, Kadaň', 'Václava Havla, Kadaň', 'Polní, Kadaň',
    'Mírové náměstí, Kadaň', 'Svatý kopeček, Kadaň', 'Suchý důl, Kadaň',
    'Želina, Kadaň', 'Prunéřov, Kadaň', 'Tušimice, Kadaň', 'Lomazice, Kadaň',
]


def fetch_json(url: str) -> dict:
    r = session.get(url, timeout=60)
    r.raise_for_status()
    return r.json()


def key_for(props: dict, renderer_field: str | None) -> str:
    if renderer_field:
        return str(props.get(renderer_field, ''))
    return json.dumps(props, ensure_ascii=False, sort_keys=True)


def color_tuple(rgba) -> tuple[float, float, float, float]:
    vals = list(rgba or [120, 120, 120, 160])
    if len(vals) == 3:
        vals.append(160)
    return tuple(max(0, min(255, float(x))) / 255 for x in vals[:4])


def geocode(query: str) -> dict | None:
    # Nominatim je použit jen pro určení bodu známých místních názvů, s povinnou prodlevou.
    r = requests.get(
        'https://nominatim.openstreetmap.org/search',
        params={'q': query + ', Česko', 'format': 'jsonv2', 'limit': 1},
        headers={'User-Agent': 'NaseKadanResearch/1.1 (+https://nasekadan.cz)'},
        timeout=30,
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0] if rows else None


def main() -> None:
    layer = fetch_json(f'{BASE}/2?f=pjson')
    legend = fetch_json(f'{BASE}/legend?f=pjson')
    geojson = fetch_json(f'{BASE}/2/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=geojson')
    raw_json = fetch_json(f'{BASE}/2/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=5514&f=json')

    (OUT / 'gis-layer.json').write_text(json.dumps(layer, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'gis-legend.json').write_text(json.dumps(legend, ensure_ascii=False, indent=2), encoding='utf-8')
    (OUT / 'gis-features.geojson').write_text(json.dumps(geojson, ensure_ascii=False), encoding='utf-8')

    renderer = ((layer.get('drawingInfo') or {}).get('renderer') or {})
    renderer_field = renderer.get('field1') or renderer.get('field')
    labels: dict[str, str] = {}
    colors: dict[str, tuple[float, float, float, float]] = {}
    for item in renderer.get('uniqueValueInfos', []):
        value = str(item.get('value', ''))
        labels[value] = str(item.get('label') or value)
        colors[value] = color_tuple(((item.get('symbol') or {}).get('color')))

    geod = Geod(ellps='WGS84')
    features = []
    area_by_value: defaultdict[str, float] = defaultdict(float)
    shapely_features = []
    for index, feature in enumerate(geojson.get('features', []), 1):
        props = feature.get('properties') or {}
        geom = shape(feature.get('geometry'))
        area, _ = geod.geometry_area_perimeter(geom)
        area = abs(float(area))
        value = key_for(props, renderer_field)
        label = labels.get(value, value)
        area_by_value[label] += area
        centroid = geom.representative_point()
        features.append({
            'index': index,
            'properties': props,
            'renderer_value': value,
            'manager_label': label,
            'area_m2': round(area, 2),
            'hectares': round(area / 10000, 4),
            'representative_point': [round(centroid.x, 7), round(centroid.y, 7)],
        })
        shapely_features.append((geom, props, label, value))

    locality_results = []
    for query in LOCALITIES:
        try:
            row = geocode(query)
            if not row:
                locality_results.append({'query': query, 'found': False})
            else:
                lon, lat = float(row['lon']), float(row['lat'])
                point = Point(lon, lat)
                matches = [
                    {'manager_label': label, 'renderer_value': value, 'properties': props}
                    for geom, props, label, value in shapely_features
                    if geom.contains(point) or geom.touches(point)
                ]
                locality_results.append({
                    'query': query, 'found': True, 'lat': lat, 'lon': lon,
                    'display_name': row.get('display_name'), 'matches': matches,
                })
        except Exception as exc:
            locality_results.append({'query': query, 'error': f'{type(exc).__name__}: {exc}'})
        time.sleep(1.05)

    # Přehledná mapa polygonů; názvy správců vycházejí přímo z rendereru městské vrstvy.
    fig, ax = plt.subplots(figsize=(13, 13))
    used = set()
    for geom, props, label, value in shapely_features:
        color = colors.get(value, (.45, .55, .45, .62))
        polygons = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
        for polygon in polygons:
            x, y = polygon.exterior.xy
            ax.fill(x, y, facecolor=color, edgecolor='black', linewidth=.22)
        used.add((value, label))
    ax.set_aspect('equal')
    ax.set_title('Kadaň – správci veřejné zeleně podle veřejného městského GIS')
    ax.set_xlabel('zeměpisná délka')
    ax.set_ylabel('zeměpisná šířka')
    handles = [Patch(facecolor=colors.get(value, (.45, .55, .45, .62)), label=label) for value, label in sorted(used)]
    if handles:
        ax.legend(handles=handles, loc='best', fontsize=8, framealpha=.92)
    fig.tight_layout()
    fig.savefig(IMAGES / 'gis-spravci-zelene-render.png', dpi=190)
    plt.close(fig)

    summary = {
        'source': f'{BASE}/2',
        'layer_name': layer.get('name'),
        'geometry_type': layer.get('geometryType'),
        'renderer_field': renderer_field,
        'renderer_labels': labels,
        'feature_count': len(features),
        'fields': layer.get('fields', []),
        'area_by_manager': [
            {'manager_label': label, 'area_m2': round(area, 2), 'hectares': round(area / 10000, 3)}
            for label, area in sorted(area_by_value.items(), key=lambda row: row[1], reverse=True)
        ],
        'features': features,
        'localities': locality_results,
        'raw_query_count': len(raw_json.get('features', [])),
    }
    (OUT / 'gis-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')

    md = ['# Veřejný GIS – správci zeleně', '', f"Vrstva: **{layer.get('name')}**", f"Počet polygonů: **{len(features)}**", '']
    md.append('## Výměra podle správce')
    md.append('')
    for row in summary['area_by_manager']:
        md.append(f"- **{row['manager_label']}**: {row['hectares']} ha")
    md.extend(['', '## Známé lokality', ''])
    for row in locality_results:
        if row.get('found'):
            names = ', '.join(m['manager_label'] for m in row.get('matches', [])) or 'bod neleží v polygonu vrstvy'
            md.append(f"- **{row['query']}**: {names}")
        else:
            md.append(f"- **{row['query']}**: nenalezeno ({row.get('error', '')})")
    (OUT / 'GIS-REPORT.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
    print(json.dumps({'feature_count': len(features), 'area_by_manager': summary['area_by_manager']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
