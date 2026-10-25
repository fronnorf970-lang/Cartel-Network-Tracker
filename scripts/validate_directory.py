#!/usr/bin/env python3
"""Read-only review of Cartel-Network-Tracker directory candidates.
Run: python scripts/validate_directory.py
No network requests. Review flags are leads, not factual determinations.
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

# Conservative text-only heuristics. They are NOT a classification model.
NON_ORGANIZATION_TERMS = (
    'energy company', 'bohemian club', 'historic lesbian bar',
    'historic nightclub', 'terrorist attack planned', 'terrorist plot',
    'nightclub in', 'cultural venue',
)


def normalize(value):
    value = unicodedata.normalize('NFKD', str(value).casefold())
    value = ''.join(c for c in value if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', value).strip()


def validate(data):
    findings = []
    def flag(severity, code, record, message):
        findings.append({'severity': severity, 'code': code,
                         'record': record, 'message': message})

    if not isinstance(data, dict) or not isinstance(data.get('nodes'), list):
        raise ValueError('Expected a JSON object containing a nodes array')
    nodes = data['nodes']
    links = data.get('links', [])
    if not isinstance(links, list):
        raise ValueError('links must be an array')
    by_id = defaultdict(list)
    by_name = defaultdict(list)
    wikidata_ids = defaultdict(list)
    imported = 0
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            flag('error', 'INVALID_NODE', f'index:{index}', 'Node is not an object')
            continue
        ident = node.get('id')
        name = node.get('name')
        label = str(ident or f'index:{index}')
        if not isinstance(ident, str) or not ident.strip():
            flag('error', 'MISSING_ID', label, 'Missing nonempty node ID')
        else:
            by_id[ident].append(label)
        if not isinstance(name, str) or not name.strip():
            flag('error', 'MISSING_NAME', label, 'Missing nonempty name')
        else:
            by_name[normalize(name)].append({'id': label, 'name': name})
        urls = node.get('source_urls', [])
        if not isinstance(urls, list) or not urls:
            flag('review', 'MISSING_SOURCE', label, 'No source URLs')
        else:
            for url in urls:
                if not isinstance(url, str) or urlparse(url).scheme not in ('http', 'https') or not urlparse(url).netloc:
                    flag('review', 'INVALID_SOURCE_URL', label, f'Check source URL: {url!r}')
        if node.get('source_type') == 'Wikidata' or str(ident).startswith('wd_'):
            imported += 1
            qid = node.get('wikidata_id')
            if not isinstance(qid, str) or not re.fullmatch(r'Q\d+', qid):
                flag('review', 'INVALID_WIKIDATA_ID', label, f'Wikidata ID: {qid!r}')
            else:
                wikidata_ids[qid].append(label)
                if ident != 'wd_' + qid:
                    flag('review', 'WIKIDATA_ID_MISMATCH', label, 'ID differs from Wikidata ID')
            if not str(node.get('description', '')).strip():
                flag('review', 'EMPTY_DESCRIPTION', label, 'No description; needs manual research')
            if node.get('entity_type') not in ('person', 'organization'):
                flag('review', 'UNKNOWN_ENTITY_TYPE', label, 'Missing or unexpected entity type')
            if not str(node.get('verification', '')).strip():
                flag('review', 'MISSING_VERIFICATION', label, 'No review/verification disclaimer')
            description = normalize(node.get('description', ''))
            if node.get('entity_type') == 'organization' and any(normalize(term) in description for term in NON_ORGANIZATION_TERMS):
                flag('review', 'POSSIBLE_MISCLASSIFICATION', label,
                     f"Description conflicts with category: {node.get('description', '')}")
    for ident, group in by_id.items():
        if len(group) > 1:
            flag('error', 'DUPLICATE_ID', ident, f'{len(group)} nodes share ID')
    for name, group in by_name.items():
        if name and len(group) > 1:
            flag('review', 'DUPLICATE_NAME', ', '.join(item['id'] for item in group),
                 'Same normalized name: ' + ', '.join(item['name'] for item in group))
    for qid, group in wikidata_ids.items():
        if len(group) > 1:
            flag('error', 'DUPLICATE_WIKIDATA_ID', qid, ', '.join(group))
    for index, link in enumerate(links):
        if not isinstance(link, dict):
            flag('error', 'INVALID_LINK', f'link:{index}', 'Link is not an object')
            continue
        for field in ('source', 'target'):
            if link.get(field) not in by_id:
                flag('error', 'BROKEN_LINK', str(link.get('id', index)),
                     f'{field} points to missing node {link.get(field)!r}')
        if not str(link.get('verification', '')).strip():
            flag('review', 'LINK_UNVERIFIED_LABEL_MISSING', str(link.get('id', index)),
                 'Relationship has no verification label')
    findings.sort(key=lambda x: (x['severity'] != 'error', x['code'], x['record']))
    return {'summary': {'nodes': len(nodes), 'imported_wikidata_nodes': imported,
                        'links': len(links), 'errors': sum(f['severity'] == 'error' for f in findings),
                        'review_flags': sum(f['severity'] == 'review' for f in findings),
                        'by_code': dict(sorted(Counter(f['code'] for f in findings).items()))},
            'findings': findings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', nargs='?', default='data/master_network.json')
    parser.add_argument('--report', default='directory_validation_report.json')
    args = parser.parse_args()
    source = Path(args.dataset)
    data = json.loads(source.read_text(encoding='utf-8'))
    report = validate(data)
    target = Path(args.report)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('DIRECTORY VALIDATION SUMMARY')
    for key, value in report['summary'].items():
        print(f'{key}: {value}')
    print(f'Full review report: {target}')
    print('NOTE: Flags are review leads, not independently verified facts.')
    return 1 if report['summary']['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
