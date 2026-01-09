"""
Minimal helper to call the ExtractedMetadata endpoint.

Usage: import and call `call_extracted_metadata(base_url, vatid, document_ids)` from your program.
Or run from the command-line to test:

  python extracted_metadata.py --url https://arquivodigitalpp.bizdocs.mobi --vatid PT504419811 --ids id1,id2

This file is intentionally minimal and mirrors the style of `auth_manager.py`.
"""

import time
import json
import argparse
import requests
import auth_manager


def call_extracted_metadata(base_url, vatid, document_ids, use_token=True, timeout=30):
    """POST to {base_url}/Company/{vatid}/Documents/ExtractedMetadata with payload {"requests": [...]}.

    - base_url: scheme+host (e.g. https://arquivodigitalpp.bizdocs.mobi) or a full endpoint that already
      contains '/Company/'. If the latter, occurrences of {vatId} or {vatid} will be replaced.
    - vatid: company VAT id string (e.g. PT504419811)
    - document_ids: list of document id strings
    - use_token: whether to fetch and send Authorization header using auth_manager
    - timeout: request timeout in seconds

    Returns: requests.Response
    """
    if not isinstance(document_ids, (list, tuple)):
        raise ValueError('document_ids must be a list of strings')

    endpoint = base_url.rstrip('/')
    if '/Company/' not in endpoint:
        endpoint = f"{endpoint}/Company/{vatid}/Documents/ExtractedMetadata"
    else:
        endpoint = endpoint.replace('{vatId}', vatid).replace('{vatid}', vatid)

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    if use_token:
        token = auth_manager.get_access_token()
        if not token:
            raise RuntimeError('Não foi possível obter token de acesso')
        try:
            expiry = auth_manager.TOKEN_INFO.get('expiry_timestamp')
            if expiry:
                print(f"A utilizar token que expira em: {time.ctime(expiry)}")
        except Exception:
            pass
        headers['Authorization'] = f'Bearer {token}'

    payload = {'requests': list(document_ids)}

    resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)

    print('URL:', endpoint)
    print('Status:', resp.status_code)
    ctype = resp.headers.get('Content-Type', '')
    if 'application/json' in ctype:
        try:
            print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        except Exception:
            print(resp.text[:400])
    else:
        print(resp.text[:400])

    return resp


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Call ExtractedMetadata endpoint with a list of document ids')
    parser.add_argument('--url', required=True, help='Base URL or full endpoint (e.g. https://arquivodigitalpp.bizdocs.mobi)')
    parser.add_argument('--vatid', default='PT504419811', help='Company VAT id (default PT504419811)')
    parser.add_argument('--ids', required=True, help='Comma-separated document ids')
    parser.add_argument('--no-token', action='store_true', help='Do not use Authorization header')
    args = parser.parse_args()

    ids = [i.strip() for i in args.ids.split(',') if i.strip()]
    call_extracted_metadata(args.url, args.vatid, ids, use_token=not args.no_token)
