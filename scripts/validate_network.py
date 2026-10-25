import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data'/'master_network.json'
g=json.loads(p.read_text(encoding='utf8'))
assert isinstance(g['nodes'],list) and isinstance(g['links'],list)
ids=[n['id'] for n in g['nodes']]
assert len(ids)==len(set(ids))
allowed={'Active Conflict','Tactical Alliance','Splinter Faction','Proxy Franchise','Neutral / Unknown'}
for e in g['links']:
    assert e['source'] in ids and e['target'] in ids
    assert e['relationship_type'] in allowed
    assert 'verification' in e
print('Network validated')
