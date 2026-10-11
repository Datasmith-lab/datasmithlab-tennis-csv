"""Export a Flashscore Tennis Actor dataset or local JSON snapshot to CSV."""
import argparse
import csv
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

FIELDS = ['id', 'startTime', 'status', 'tour', 'tournament', 'surface',
          'matchType', 'homePlayer', 'awayPlayer', 'score', 'winner',
          'resultType', 'sets', 'url']


def fetch_rows(dataset_id, max_rows):
    token = os.environ.get('APIFY_TOKEN')
    if not token:
        raise ValueError('Set APIFY_TOKEN in your environment; do not put it in a file.')
    rows = []
    while len(rows) <= max_rows:
        limit = min(1000, max_rows + 1 - len(rows))
        url = ('https://api.apify.com/v2/datasets/' + quote(dataset_id, safe='') +
               f'/items?clean=true&offset={len(rows)}&limit={limit}')
        request = Request(url, headers={'Authorization': 'Bearer ' + token})
        try:
            with urlopen(request, timeout=60) as response:
                batch = json.load(response)
        except HTTPError as exc:
            raise ValueError(f'Apify HTTP {exc.code}; check access and dataset ID.') from None
        except URLError:
            raise ValueError('Apify connection failed; no CSV written.') from None
        if not isinstance(batch, list):
            raise ValueError('Expected a dataset array.')
        rows.extend(batch)
        if not batch or len(rows) > max_rows:
            break
    return rows


def cell(value):
    if value is None:
        return ''
    if isinstance(value, (list, dict)):
        value = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    text = str(value)
    # Guard CSV import into spreadsheet programs against formula evaluation.
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text


def export(rows, output, max_rows):
    if not isinstance(rows, list) or len(rows) > max_rows:
        raise ValueError('Expected an array within --max-rows; no CSV written.')
    ids = set()
    for row in rows:
        if (not isinstance(row, dict) or not isinstance(row.get('id'), str)
                or not row['id'] or not row.get('homePlayer')
                or not row.get('awayPlayer') or row['id'] in ids):
            raise ValueError('Missing match fields or duplicate IDs; no CSV written.')
        ids.add(row['id'])
    if output.exists():
        raise ValueError('Output already exists; choose a new path.')
    with output.open('x', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: cell(row.get(key)) for key in FIELDS})
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--input', type=Path, help='Local Actor dataset JSON array')
    source.add_argument('--dataset-id', help='Dataset from a completed Actor run')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-rows', type=int, default=1000)
    args = parser.parse_args()
    try:
        if not 1 <= args.max_rows <= 100000:
            raise ValueError('--max-rows must be between 1 and 100000.')
        rows = (json.loads(args.input.read_text(encoding='utf-8-sig')) if args.input
                else fetch_rows(args.dataset_id, args.max_rows))
        count = export(rows, args.output, args.max_rows)
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')
    print(f'Exported {count} unique matches to {args.output}.')


if __name__ == '__main__':
    main()
