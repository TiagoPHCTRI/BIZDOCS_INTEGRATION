"""
Minimal helper to call the ExtractedMetadata endpoint.

This script is intentionally minimal and follows the `auth_manager` style you requested.

Defaults and placeholders:
- Default VAT id: PT504419811
- Default api-bzd: https://nikepp.azurewebsites.net/api/

The script accepts a base URL or a template using placeholders like
  {{api-bzd}} and {{api-bzd-companyvatid}}.

Example endpoint template you provided:
  {{api-bzd}}/Company/{{api-bzd-companyvatid}}/Documents/ExtractedMetadata

Usage (PowerShell):
  python main.py --url "{{api-bzd}}" --ids id1,id2
  python main.py --url https://nikepp.azurewebsites.net/api/ --ids id1,id2 --no-token

If you want machine-readable output for Visual FoxPro, use --machine-json which prints a single-line JSON
with status, url and body (body is JSON if response Content-Type is application/json, otherwise a truncated text).
"""

import os
import re
import time
import json
import argparse
import requests
import auth_manager


DEFAULT_API_BZD = os.environ.get('API_BZD', 'https://nikepp.azurewebsites.net/api/')
DEFAULT_VATID = os.environ.get('API_BZD_COMPANYVATID', 'PT504419811')

# --- User-editable defaults: put your base URL, VAT id and example document ids here ---
# Keep DOCUMENT_IDS empty; you'll receive these ids from your method and can either set them
# here or pass via --ids when running the script.
BASE_URL = DEFAULT_API_BZD
VATID = DEFAULT_VATID
DOCUMENT_IDS = []  # e.g. ['abc-123', 'def-456']
IN_ACCOUNTING_ITEMS = []  # populated by call_in_accounting()
DEBUG = False
IN_ACCOUNTING_RESPONSE = None  # full parsed response object (items + paginationKey)


def apply_placeholders(s: str, vars_map: dict):
    if not isinstance(s, str):
        return s
    out = s
    for m in re.findall(r"\{\{([^}]+)\}\}", s):
        key = m.strip()
        if key in vars_map:
            out = out.replace('{{' + key + '}}', vars_map[key])
        else:
            env = os.environ.get(key)
            if env is not None:
                out = out.replace('{{' + key + '}}', env)
    return out


def build_extracted_metadata_endpoint(base_or_template: str, vatid: str, vars_map: dict):
    # apply placeholders if present
    resolved = apply_placeholders(base_or_template, vars_map)
    resolved = resolved.rstrip('/')
    if '/Company/' in resolved:
        # already a full path; ensure vatid placeholders replaced
        resolved = resolved.replace('{vatId}', vatid).replace('{vatid}', vatid)
        return resolved
    # otherwise assume it's a base URL (scheme+host+maybe /api)
    return f"{resolved}/Company/{vatid}/Documents/ExtractedMetadata"


def call_extracted_metadata(vatid=None, timeout=30, vars_map=None):
    """Call the ExtractedMetadata endpoint.

    Signature: call_extracted_metadata(vatid)

    - vatid: company VAT id to use for this call. If omitted, uses module VATID.
    The function reads document ids and base URL from module-level variables.
    """
    # resolve vatid and other module-level values
    vatid = vatid or VATID
    base_url = BASE_URL
    document_ids = list(DOCUMENT_IDS)

    if not isinstance(document_ids, (list, tuple)) or not document_ids:
        raise ValueError('DOCUMENT_IDS must be a non-empty list or tuple of document id strings')

    vars_map = vars_map or {}
    # defaults
    vars_map.setdefault('api-bzd', DEFAULT_API_BZD)
    vars_map.setdefault('api-bzd-companyvatid', DEFAULT_VATID)

    endpoint = build_extracted_metadata_endpoint(base_url, vatid, vars_map)

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    # always use token
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

    return resp


def call_in_accounting(vatid=None, payload=None, timeout=30, vars_map=None):
    """Call the Documents/InAccounting endpoint and store returned items in module variable.

    - vatid: company VAT id (defaults to module VATID)
    - payload: dict to send; if None, uses the default body provided by user
    """
    vatid = vatid or VATID
    base_url = BASE_URL

    vars_map = vars_map or {}
    vars_map.setdefault('api-bzd', DEFAULT_API_BZD)
    vars_map.setdefault('api-bzd-companyvatid', DEFAULT_VATID)

    # build endpoint
    resolved = apply_placeholders(base_url, vars_map)
    resolved = resolved.rstrip('/')
    if '/Company/' in resolved:
        endpoint = resolved.replace('{vatId}', vatid).replace('{vatid}', vatid)
        # ensure path ends with Documents/InAccounting
        if not endpoint.endswith('/Documents/InAccounting'):
            endpoint = endpoint.rstrip('/') + '/Documents/InAccounting'
    else:
        endpoint = f"{resolved}/Company/{vatid}/Documents/InAccounting"

    # mirror Postman headers precisely to avoid server-side differences
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json; charset=utf-8',
        'Request-Context': 'appId=',
        'User-Agent': 'PostmanRuntime/7.29.0'
    }
    token = auth_manager.get_access_token()
    if not token:
        raise RuntimeError('Não foi possível obter token de acesso')
    headers['Authorization'] = f'Bearer {token}'

    if payload is None:
        payload = {
            "documentStatus": [
                "accountvalidation",
                "manualentry"
            ]
        }

    try:
        if DEBUG:
            print('--- InAccounting REQUEST ---')
            print('URL:', endpoint)
            print('Headers:', json.dumps(headers, ensure_ascii=False))
            print('Payload:', json.dumps(payload, ensure_ascii=False, indent=2))
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
    except Exception as e:
        print(f'Erro ao executar POST: {e}')
        raise

    if DEBUG:
        try:
            req_body = getattr(resp.request, 'body', None)
            print('--- RESPONSE ---')
            print('Status:', resp.status_code)
            print('Response headers:', dict(resp.headers))
            print('Response body:', resp.text[:4000])
            print('Request body sent:', req_body[:4000] if isinstance(req_body, (bytes, str)) else req_body)
        except Exception:
            pass

    # try to extract list of items from response JSON
    items = []
    try:
        data = resp.json()
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            # common keys that might contain items
            for key in ('items', 'results', 'data', 'documents'):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            else:
                # fallback: find first list value in dict
                for v in data.values():
                    if isinstance(v, list):
                        items = v
                        break
    except Exception:
        # response not JSON or parsing failed; keep items empty
        items = []

    # store in module-level variable for later iteration
    global IN_ACCOUNTING_ITEMS
    IN_ACCOUNTING_ITEMS = items

    # build canonical response object with items and optional paginationKey
    pagination_key = None
    try:
        if isinstance(data, dict) and 'paginationKey' in data:
            pagination_key = data.get('paginationKey')
    except Exception:
        pagination_key = None

    response_obj = {
        'items': items,
        'paginationKey': pagination_key
    }

    # store full response object in module-level variable
    global IN_ACCOUNTING_RESPONSE
    IN_ACCOUNTING_RESPONSE = response_obj

    # persist to disk for external processes (e.g., Visual FoxPro) — safe write
    try:
        save_path = r'C:\temp\in_accounting.json'
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as fh:
            json.dump(response_obj, fh, ensure_ascii=False, indent=2)
    except Exception:
        # don't fail the call if writing to disk fails; just warn when in debug
        if DEBUG:
            print('Warning: failed to persist InAccounting JSON to disk')

    return resp


def get_in_accounting_response():
    """Return the last stored full InAccounting response object.

    Returns a dict with keys `items` (list) and `paginationKey` (or None).
    """
    return IN_ACCOUNTING_RESPONSE


def get_in_accounting_items():
    """Return the last populated IN_ACCOUNTING_ITEMS list.

    Useful for external callers (e.g., Visual FoxPro) that import this module and
    want to iterate over the results after `call_in_accounting()` has run.
    """
    return IN_ACCOUNTING_ITEMS


def print_in_accounting_summary(limit: int = None):
    """Print a concise, human-readable summary of the items stored in
    `IN_ACCOUNTING_ITEMS`.

    Each line shows: index, documentId, documentNumber, documentName,
    documentTotalAmount and documentStatus.
    """
    items = IN_ACCOUNTING_ITEMS
    if not items:
        print('IN_ACCOUNTING_ITEMS is empty')
        return
    for i, it in enumerate(items):
        if limit is not None and i >= limit:
            break
        doc_id = it.get('documentId', '')
        number = it.get('documentNumber', '')
        name = it.get('documentName', '')
        amount = it.get('documentTotalAmount', '')
        status = it.get('documentStatus', '')
        print(f"{i+1}. id={doc_id} number={number} name={name} amount={amount} status={status}")


def export_in_accounting_csv(path: str):
    """Export `IN_ACCOUNTING_ITEMS` to CSV at `path`.

    Returns the path on success.
    """
    import csv

    items = IN_ACCOUNTING_ITEMS
    if not items:
        raise ValueError('IN_ACCOUNTING_ITEMS is empty; run call_in_accounting() first')

    fieldnames = [
        'documentId', 'documentNumber', 'documentName', 'documentTotalAmount',
        'documentStatus', 'documentDate', 'documentVendorVatId', 'documentCustomerVatId'
    ]
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for it in items:
            row = {k: it.get(k, '') for k in fieldnames}
            writer.writerow(row)
    return path


def _print_response(resp: requests.Response, machine_json: bool = False):
    endpoint = getattr(resp.request, 'url', None) or ''
    status = resp.status_code
    ctype = resp.headers.get('Content-Type', '')
    body = None
    if 'application/json' in ctype:
        try:
            body = resp.json()
        except Exception:
            body = resp.text
    else:
        body = resp.text

    if machine_json:
        out = {'status': status, 'url': endpoint}
        # include body as JSON if possible, else truncated text
        if isinstance(body, (dict, list)):
            out['body'] = body
        else:
            out['body'] = (body or '')[:200]
        print(json.dumps(out, ensure_ascii=False))
    else:
        print('URL:', endpoint)
        print('Status:', status)
        if isinstance(body, (dict, list)):
            print(json.dumps(body, ensure_ascii=False, indent=2))
        else:
            print(body[:400])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Call ExtractedMetadata with token check and simple defaults')
    parser.add_argument('--url', default=BASE_URL, help='Base URL or template (default from BASE_URL)')
    parser.add_argument('--vatid', default=VATID, help='Company VAT id (default from VATID)')
    parser.add_argument('--ids', help='Comma-separated document ids; if omitted uses DOCUMENT_IDS variable')
    parser.add_argument('--run-inaccounting', action='store_true', help='Also run the Documents/InAccounting method and store items')
    parser.add_argument('--debug', action='store_true', help='Enable verbose request/response logging for debugging')
    parser.add_argument('--machine-json', action='store_true', help='Print single-line JSON summary (for VFP)')
    args = parser.parse_args()

    # If CLI provided values, write them to module globals so the function can use them
    if args.url:
        BASE_URL = args.url  # local override for this invocation
    if args.vatid:
        VATID = args.vatid
    if args.ids:
        DOCUMENT_IDS[:] = [i.strip() for i in args.ids.split(',') if i.strip()]
    if args.debug:
        DEBUG = True

    # New behavior: obtain token (if needed) and run only call_in_accounting()
    SAFETY_MARGIN = 60
    current_token = auth_manager.TOKEN_INFO.get('access_token')
    expiry = auth_manager.TOKEN_INFO.get('expiry_timestamp', 0)
    if current_token and (expiry > time.time() + SAFETY_MARGIN):
        print(f"Usando token existente que expira em: {time.ctime(expiry)}")
    else:
        print('Token ausente ou expirado; a obter novo token...')
        new_token = auth_manager.get_access_token()
        if not new_token:
            raise SystemExit('Não foi possível obter token de acesso')

    # Execute only the InAccounting call as requested by the user
    resp = call_in_accounting(vatid=VATID)
    # Print response (machine-json option still supported)
    _print_response(resp, machine_json=args.machine_json)
    
    # Print a short summary of items (human-friendly) unless machine-json requested
    if not args.machine_json:
        print(f"InAccounting returned {len(IN_ACCOUNTING_ITEMS)} items")
        print_in_accounting_summary(limit=20)

    # Build canonical response object directly from resp.json()
    try:
        data = resp.json()
    except Exception:
        data = None

    # locate items whether response is {'items': [...]} or list itself
    if isinstance(data, dict):
        items = data.get('items') or next((v for v in data.values() if isinstance(v, list)), [])
    elif isinstance(data, list):
        items = data
    else:
        items = []

    canonical_items = []
    for it in items:
        canonical_items.append({
            "journalGroupName": it.get("journalGroupName", ""),
            "accountancyYear": it.get("accountancyYear", 0) or 0,
            "accountancyMonth": it.get("accountancyMonth", 0) or 0,
            "costCenter": it.get("costCenter", ""),
            "documentDate": it.get("documentDate", ""),
            "documentNumber": it.get("documentNumber", ""),
            "documentVendorVatId": it.get("documentVendorVatId", ""),
            "documentCustomerVatId": it.get("documentCustomerVatId", ""),
            "documentTotalAmount": it.get("documentTotalAmount", 0) or 0,
            "documentStatus": it.get("documentStatus", ""),
            "updatedOn": it.get("updatedOn", ""),
            "documentId": it.get("documentId", ""),
            "createdOn": it.get("createdOn", ""),
            "documentName": it.get("documentName", "")
        })

    result = {
        "items": canonical_items,
        "paginationKey": (data.get('paginationKey') if isinstance(data, dict) else None)
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
# End of script