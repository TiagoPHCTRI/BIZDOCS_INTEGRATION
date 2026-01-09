"""
Run a Postman-style request object.

Usage:
  from postman_runner import run_postman_request
  req = {
      'method': 'POST',
      'url': '{{api-bzd}}/Company/{{api-bzd-companyvatid}}/Documents/ExtractedMetadata',
      'headers': {'Content-Type': 'application/json'},
      'body': {'requests': ['id1','id2']}
  }
  resp = run_postman_request(req)

This helper resolves {{...}} placeholders (using environment variables or defaults),
injects Authorization Bearer token from auth_manager if requested, and sends the request.
"""

import os
import re
import json
import time
import requests
import auth_manager

DEFAULTS = {
    'api-bzd': os.environ.get('API_BZD', 'https://nikepp.azurewebsites.net/api/'),
    'api-bzd-companyvatid': os.environ.get('API_BZD_COMPANYVATID', 'PT504419811')
}


def _apply_placeholders(s: str, vars_map: dict):
    if not isinstance(s, str):
        return s
    out = s
    for m in re.findall(r"\{\{([^}]+)\}\}", s):
        key = m.strip()
        if vars_map and key in vars_map:
            out = out.replace('{{' + key + '}}', vars_map[key])
        else:
            env = os.environ.get(key)
            if env is not None:
                out = out.replace('{{' + key + '}}', env)
            elif key in DEFAULTS:
                out = out.replace('{{' + key + '}}', DEFAULTS[key])
    return out


def run_postman_request(req_obj: dict, use_token: bool = True, timeout: int = 30, vars_map: dict = None) -> requests.Response:
    """Execute a request described by a dict similar to Postman's exported request.

    req_obj keys supported: method, url, headers (dict), body (dict|string)
    """
    if not isinstance(req_obj, dict):
        raise ValueError('req_obj must be a dict')

    method = req_obj.get('method', 'GET').upper()
    raw_url = req_obj.get('url') or req_obj.get('rawUrl') or ''
    vars_map = vars_map or {}
    url = _apply_placeholders(raw_url, vars_map)

    headers = dict(req_obj.get('headers') or {})

    # inject token if requested and not already set
    if use_token:
        token = auth_manager.get_access_token()
        if not token:
            raise RuntimeError('Não foi possível obter token de acesso')
        if 'Authorization' not in {k.title(): v for k, v in headers.items()}:
            headers['Authorization'] = f'Bearer {token}'

    body = req_obj.get('body')

    # Decide how to send body
    send_kwargs = {'headers': headers, 'timeout': timeout}
    ctype = headers.get('Content-Type', '')
    if body is None:
        resp = requests.request(method, url, **send_kwargs)
    else:
        # If body is a dict and content-type is json, send as json
        if isinstance(body, (dict, list)) or 'application/json' in ctype:
            send_kwargs['json'] = body
        else:
            # send as raw text
            if isinstance(body, dict):
                send_kwargs['data'] = json.dumps(body)
            else:
                send_kwargs['data'] = body
        resp = requests.request(method, url, **send_kwargs)

    return resp


if __name__ == '__main__':
    print('postman_runner helper. Import run_postman_request(req_obj) to use.')
