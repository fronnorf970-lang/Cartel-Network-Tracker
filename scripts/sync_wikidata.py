"""Fetch descriptive public Wikidata metadata for manually selected QIDs.
No automated assertions about leadership, conflict, routes, or territorial control.
"""
import json
import urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
# These QIDs are configuration, not automatically inferred matches. Edit only after checking.
CONFIG = ROOT / 'data' / 'wikidata_ids.json'
OUTPUT = ROOT / 'data' / 'wiki_entities.json'
ids = json.loads(CONFIG.read_text(encoding='utf8'))
result = {'entities': [], 'note': 'Public Wikidata descriptions only; review before incorporating into master baseline.'}
for qid in ids:
    if not (qid.startswith('Q') and qid[1:].isdigit()):
        continue
    url = f'https://www.wikidata.org/wiki/Special:EntityData/{qid}.json'
    request = urllib.request.Request(url, headers={'User-Agent':'FactionNetworkResearchDemo/1.0 (GitHub Pages educational project)'})
    with urllib.request.urlopen(request, timeout=20) as response:
        entity = json.load(response)['entities'][qid]
    labels = entity.get('labels', {})
    descriptions = entity.get('descriptions', {})
    result['entities'].append({
        'qid': qid,
        'name': labels.get('en', labels.get('es', {})).get('value', qid),
        'description': descriptions.get('en', descriptions.get('es', {})).get('value', ''),
        'source_url': f'https://www.wikidata.org/wiki/{qid}',
        'lastrevid': entity.get('lastrevid'),
    })
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(f'Updated {len(result["entities"])} public descriptions')
