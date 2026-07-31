#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests
from pyproj import Transformer, Geod
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, shape
from shapely.ops import transform

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.github' / 'research' / 'greenery-kadan-2026'
GEOJSON = OUT / 'gis-features.geojson'

WGS_TO_METRIC = Transformer.from_crs('EPSG:4326', 'EPSG:5514', always_xy=True).transform
METRIC_TO_WGS = Transformer.from_crs('EPSG:5514', 'EPSG:4326', always_xy=True).transform
GEOD = Geod(ellps='WGS84')

OVERPASS_ENDPOINTS = [
    'https://overpass-api.de/api/interpreter',
    'https://overpass.kumi.systems/api/interpreter',
    'https://overpass.nchc.org.tw/api/interpreter',
]


def metric(geom):
    return transform(WGS_TO_METRIC, geom)


def fetch_overpass(bbox: tuple[float, float, float, float]) -> dict:
    south, west, north, east = bbox
    query = f'''[out:json][timeout:180];
(
  way["highway"]["name"]({south},{west},{north},{east});
  way["leisure"]["name"]({south},{west},{north},{east});
  way["landuse"]["name"]({south},{west},{north},{east});
  way["place"]["name"]({south},{west},{north},{east});
  relation["place"]["name"]({south},{west},{north},{east});
  relation["leisure"]["name"]({south},{west},{north},{east});
  node["place"]["name"]({south},{west},{north},{east});
  node["amenity"]["name"]({south},{west},{north},{east});
  node["shop"]["name"]({south},{west},{north},{east});
);
out tags center geom;'''
    errors = []
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            r = requests.post(endpoint, data={'data': query}, headers={'User-Agent':'NaseKadanResearch/1.2 (+https://nasekadan.cz)'}, timeout=240)
            if r.status_code in (429, 502, 503, 504):
                errors.append(f'{endpoint}: HTTP {r.status_code}')
                time.sleep(10)
                continue
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            errors.append(f'{endpoint}: {type(exc).__name__}: {exc}')
    raise RuntimeError('; '.join(errors))


def osm_geometry(element: dict):
    geom = element.get('geometry') or []
    if geom:
        coords = [(float(p['lon']), float(p['lat'])) for p in geom]
        if len(coords) >= 4 and coords[0] == coords[-1]:
            try:
                poly = Polygon(coords)
                if poly.is_valid and not poly.is_empty:
                    return poly
            except Exception:
                pass
        if len(coords) >= 2:
            return LineString(coords)
        if len(coords) == 1:
            return Point(coords[0])
    center = element.get('center')
    if center:
        return Point(float(center['lon']), float(center['lat']))
    if 'lon' in element and 'lat' in element:
        return Point(float(element['lon']), float(element['lat']))
    return None


def tag_type(tags: dict) -> str:
    for key in ('highway','leisure','landuse','place','amenity','shop'):
        if tags.get(key):
            return f'{key}:{tags[key]}'
    return 'named'


def relevance(component_m, feature_m, geom_type: str) -> tuple[float, float]:
    if feature_m.geom_type in ('Polygon','MultiPolygon'):
        inter = component_m.intersection(feature_m)
        return float(inter.area), float(component_m.distance(feature_m))
    if feature_m.geom_type in ('LineString','MultiLineString'):
        # Vegetation polygons often stop at the curb. A 25 m road buffer identifies adjoining green areas.
        buffered = feature_m.buffer(25)
        inter = component_m.intersection(buffered)
        return float(inter.area), float(component_m.distance(feature_m))
    return 0.0, float(component_m.distance(feature_m))


def main() -> None:
    data = json.loads(GEOJSON.read_text(encoding='utf-8'))
    all_geom = [shape(f['geometry']) for f in data.get('features', [])]
    union_bounds = MultiPolygon([p for g in all_geom for p in (list(g.geoms) if g.geom_type == 'MultiPolygon' else [g])]).bounds
    west, south, east, north = union_bounds
    bbox = (south - .01, west - .01, north + .01, east + .01)

    overpass_error = ''
    try:
        osm = fetch_overpass(bbox)
    except Exception as exc:
        osm = {'elements': []}
        overpass_error = f'{type(exc).__name__}: {exc}'

    named = []
    for el in osm.get('elements', []):
        tags = el.get('tags') or {}
        name = tags.get('name')
        if not name:
            continue
        geom = osm_geometry(el)
        if geom is None or geom.is_empty:
            continue
        named.append({
            'name': name,
            'type': tag_type(tags),
            'tags': tags,
            'geometry': geom,
            'geometry_metric': metric(geom),
        })

    rows = []
    manager_summary = defaultdict(lambda: {'components':0,'area_m2':0.0,'nearby':Counter()})
    for feature in data.get('features', []):
        props = feature.get('properties') or {}
        manager = props.get('nazev') or 'neuvedeno'
        geom = shape(feature['geometry'])
        parts = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
        for component_index, part in enumerate(sorted(parts, key=lambda g:g.area, reverse=True), 1):
            part_m = metric(part)
            point = part.representative_point()
            candidates = []
            for item in named:
                overlap, distance = relevance(part_m, item['geometry_metric'], item['type'])
                if overlap > 0 or distance <= 250:
                    score = overlap * 1000 - distance
                    candidates.append({
                        'name': item['name'], 'type': item['type'],
                        'overlap_m2': round(overlap,2), 'distance_m': round(distance,2),
                        'score': score,
                    })
            candidates.sort(key=lambda x:(x['overlap_m2'] > 0, x['overlap_m2'], -x['distance_m']), reverse=True)
            best = candidates[:8]
            area = float(part_m.area)
            row = {
                'manager': manager,
                'component': component_index,
                'area_m2': round(area,2),
                'hectares': round(area/10000,4),
                'representative_lon': round(point.x,7),
                'representative_lat': round(point.y,7),
                'bounds': [round(x,7) for x in part.bounds],
                'nearby_names': best,
            }
            rows.append(row)
            manager_summary[manager]['components'] += 1
            manager_summary[manager]['area_m2'] += area
            for candidate in best[:4]:
                weight = max(1, int(candidate['overlap_m2']/1000)) if candidate['overlap_m2'] else 1
                manager_summary[manager]['nearby'][candidate['name']] += weight

    rows.sort(key=lambda x:(x['manager'], -x['area_m2']))
    output = {
        'source': str(GEOJSON.relative_to(ROOT)),
        'overpass_error': overpass_error,
        'osm_named_features': len(named),
        'total_components': len(rows),
        'managers': [
            {
                'manager': manager,
                'components': value['components'],
                'area_m2': round(value['area_m2'],2),
                'hectares': round(value['area_m2']/10000,3),
                'most_relevant_names': [name for name,_ in value['nearby'].most_common(25)],
            }
            for manager,value in sorted(manager_summary.items(), key=lambda x:x[1]['area_m2'], reverse=True)
        ],
        'components': rows,
    }
    (OUT/'gis-components.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')

    with (OUT/'gis-components.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter=';')
        w.writerow(['správce','plocha','m2','ha','lon','lat','nejbližší názvy'])
        for row in rows:
            names=', '.join(dict.fromkeys(c['name'] for c in row['nearby_names'][:6]))
            w.writerow([row['manager'],row['component'],row['area_m2'],row['hectares'],row['representative_lon'],row['representative_lat'],names])

    md=['# Jednotlivé plochy veřejné zeleně podle správce','',f"Vícečástové GIS objekty se rozpadají na **{len(rows)} samostatných polygonů**. Přiřazení správce je přímo z městské vrstvy; názvy okolních ulic a míst jsou pomocné orientační údaje z OpenStreetMap.",'']
    if overpass_error:
        md += [f'> OSM doplnění selhalo: {overpass_error}','']
    for manager in sorted(manager_summary, key=lambda m:manager_summary[m]['area_m2'], reverse=True):
        subset=[r for r in rows if r['manager']==manager]
        total=manager_summary[manager]['area_m2']
        md += [f"## {manager}",'',f"- **{len(subset)} samostatných ploch**, celkem **{total/10000:.3f} ha**.",'']
        for row in subset:
            names=', '.join(dict.fromkeys(c['name'] for c in row['nearby_names'][:5])) or 'bez spolehlivého názvu v okolí'
            md.append(f"- Plocha {row['component']}: **{row['hectares']} ha**, bod {row['representative_lat']}, {row['representative_lon']} - {names}")
        md.append('')
    (OUT/'GIS-COMPONENTS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'components':len(rows),'osm_features':len(named),'error':overpass_error},ensure_ascii=False))

if __name__=='__main__':
    main()
