"""Discover publicly catalogued organizations and people from Wikidata.
Never creates relationship edges or claims current operational status.
Runs in GitHub Actions and proposes a PR for human review.
"""
import json, time, urllib.parse, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'data'/'master_network.json'
# Wikidata class identifiers: gang, criminal organization, organized crime group,
# drug trafficking organization, Mexican cartel, mafia, outlaw motorcycle club.
CLASSES={'Q275186':'Gang','Q1788992':'Criminal organization','Q4335775':'Organized crime group','Q5308925':'Drug trafficking organization','Q21234891':'Mexican cartel','Q18550':'Mafia','Q1849110':'Outlaw motorcycle club'}
# For people, limit to explicitly classified crime figures (occupation), not family members.
PERSON_OCCUPATIONS={'Q2429253':'Gangster','Q1254956':'Drug lord'}
QUERY_ENDPOINT='https://query.wikidata.org/sparql'

def fetch(query):
    url=QUERY_ENDPOINT+'?'+urllib.parse.urlencode({'query':query,'format':'json'})
    req=urllib.request.Request(url,headers={'User-Agent':'FactionNetworkTrackerResearch/3.0 (public GitHub Pages directory; contact via repository issues)','Accept':'application/sparql-results+json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=65) as r:return json.load(r)['results']['bindings']
        except Exception:
            if attempt==2:raise
            time.sleep(5*(attempt+1))

def query_class(qid,person=False):
    # Scope by country of citizenship for persons; location/country for organizations.
    # Some entries lack location claims; this is a broad discovery index, not exhaustive.
    geographic='?item wdt:P27 wd:Q96 .' if person else '{ ?item wdt:P17 ?country . } UNION { ?item wdt:P131/wdt:P17 ?country . } UNION { ?item wdt:P495 ?country . }'
    if person:
        geographic='?item wdt:P27 ?country .'
    predicate='wdt:P106' if person else 'wdt:P31/wdt:P279*'
    return f'''SELECT DISTINCT ?item ?itemLabel ?description ?country WHERE {{
      ?item {predicate} wd:{qid} .
      {geographic}
      VALUES ?country {{ wd:Q96 wd:Q30 }}
      OPTIONAL {{ ?item schema:description ?description FILTER(LANG(?description)="en") }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en,es". }}
    }} LIMIT 1800'''

def main():
    obj=json.loads(DEST.read_text(encoding='utf8'))
    old={n['id']:n for n in obj['nodes']}
    results={}
    failures=[]
    for qid,category in list(CLASSES.items())+list(PERSON_OCCUPATIONS.items()):
        person=qid in PERSON_OCCUPATIONS
        try:
            for row in fetch(query_class(qid,person)):
                uri=row['item']['value']; ident=uri.rsplit('/',1)[-1]
                if not ident.startswith('Q') or not ident[1:].isdigit():continue
                name=row.get('itemLabel',{}).get('value',ident)
                if name==ident:continue
                country=row['country']['value'].rsplit('/',1)[-1]
                key='wd_'+ident
                if key in results:continue
                results[key]={'id':key,'name':name,'tier':('Person — '+category if person else category),
                    'entity_type':'person' if person else 'organization',
                    'regions':['Mexico' if country=='Q96' else 'United States'],
                    'description':row.get('description',{}).get('value',''),
                    'source_urls':[uri], 'verification':'Wikidata classification; unreviewed, historical/current status unknown',
                    'source_type':'Wikidata','wikidata_id':ident}
        except Exception as exc:
            failures.append(f'{qid}: {exc}')
        time.sleep(2)
   

if __name__=='__main__':main()
