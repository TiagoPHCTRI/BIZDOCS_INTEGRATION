# main.py
"""
Main de demonstração para chamar APIs protegidas, processar respostas por tipo
e gerar relatórios em PDF com metadados, pedido/resposta e sumário.

Funcionalidades adicionadas:
- Mapeamento de processadores por tipo de conteúdo
- Geração de PDF (em ./reports) com informações detalhadas
- Função de exemplo `simulate_responses` para gerar relatórios locais

Leia o README.md para detalhes de campos do PDF e como estender os processadores.
"""

import os
import time
import json
import requests
import auth_manager
from response_processors import process_response
from pdf_utils import generate_api_report_pdf
import typing
import argparse
import pathlib
import urllib.parse


def _load_method_from_postman(postman_path: str, method_name: str) -> typing.Tuple[str, str, typing.Optional[dict]]:
    """Carrega um método por nome a partir de uma Postman collection exportada.

    Procura recursivamente por um item cujo `name` corresponde a `method_name`.
    Retorna (url, method, payload_template).
    """
    try:
        with open(postman_path, 'r', encoding='utf-8') as f:
            col = json.load(f)
    except Exception as e:
        raise

    def find_item(items, target):
        for it in items:
            if it.get('name') == target and 'request' in it:
                return it
            # nested
            if 'item' in it and isinstance(it['item'], list):
                found = find_item(it['item'], target)
                if found:
                    return found
        return None

    root_items = col.get('item', [])
    item = find_item(root_items, method_name)
    if not item:
        # try to interpret method_name as path with slashes
        parts = method_name.split('/')
        def find_by_path(items, parts):
            if not parts:
                return None
            name = parts[0]
            for it in items:
                if it.get('name') == name:
                    if len(parts) == 1:
                        return it
                    if 'item' in it:
                        return find_by_path(it['item'], parts[1:])
            return None
        item = find_by_path(root_items, parts)

    # if still not found, try partial/case-insensitive match over request items
    if not item:
        lower = method_name.lower()
        def find_partial(items):
            for it in items:
                if 'request' in it and lower in (it.get('name') or '').lower():
                    return it
                if 'item' in it:
                    found = find_partial(it['item'])
                    if found:
                        return found
            return None
        item = find_partial(root_items)

    if not item or 'request' not in item:
        raise KeyError(f"Method '{method_name}' not found in Postman collection")

    req = item['request']
    method = req.get('method', 'GET')
    # extract URL: prefer raw then construct
    url = None
    url_obj = req.get('url')
    if isinstance(url_obj, dict):
        url = url_obj.get('raw')
        if not url:
            # try host + path
            host = ''.join(url_obj.get('host', []) or [])
            path = '/'.join(url_obj.get('path', []) or [])
            if host:
                url = host.rstrip('/') + '/' + path.lstrip('/')
    elif isinstance(url_obj, str):
        url = url_obj

    # body template
    payload = None
    body = req.get('body')
    if isinstance(body, dict):
        raw = body.get('raw')
        if raw:
            try:
                payload = json.loads(raw)
            except Exception:
                # keep as string if not JSON
                payload = raw

    return url, method, payload


def call_protected_api_and_report(url, method='GET', payload=None, out_dir='reports'):
    """Chama a API usando token obtido por `auth_manager`, processa a resposta
    usando `response_processors` e gera um PDF de relatório em `out_dir`.
    """
    os.makedirs(out_dir, exist_ok=True)

    access_token = auth_manager.get_access_token()
    if not access_token:
        raise RuntimeError("Não foi possível obter um token de acesso.")

    # Mostrar validade do token (como antes)
    try:
        expiry = auth_manager.TOKEN_INFO.get('expiry_timestamp')
        if expiry:
            print(f"A utilizar token que expira em: {time.ctime(expiry)}")
    except Exception:
        # Não falhar por causa da impressão de validade
        pass

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    if method.upper() == 'GET':
        resp = requests.get(url, headers=headers)
    else:
        headers['Content-Type'] = 'application/json'
        resp = requests.request(method, url, headers=headers, json=payload)

    timestamp = time.time()

    # Construir objetos de metadados/req/resp para o PDF
    metadata = {
        'generated_at': time.ctime(timestamp),
        'api_endpoint': url,
        'method': method.upper(),
    }

    request_info = {
        'headers': dict(resp.request.headers) if resp.request is not None else {},
        'body_summary': (json.dumps(payload, ensure_ascii=False, indent=2) if payload else None),
    }

    # Processar a resposta (detecção do tipo + processamento específico)
    proc_result = process_response(resp)

    response_info = {
        'status_code': resp.status_code,
        'headers': dict(resp.headers),
        'detected_type': proc_result.get('type'),
        'summary': proc_result.get('summary'),
        'artifact': proc_result.get('artifact'),
    }

    # Nome do ficheiro de saída
    safe_endpoint = url.replace('://', '_').replace('/', '_')
    out_pdf = os.path.join(out_dir, f"report_{safe_endpoint}_{int(timestamp)}.pdf")

    generate_api_report_pdf(out_pdf, metadata, request_info, response_info, notes=proc_result.get('notes'))

    print(f"PDF gerado: {out_pdf}")
    return out_pdf


def simulate_responses(out_dir='reports'):
    """Gera exemplos de relatórios usando vários tipos de resposta simulados.

    Útil para validar os processadores e inspecionar o layout do PDF.
    """
    os.makedirs(out_dir, exist_ok=True)

    # Dummy response object para testes offline
    class DummyResponse:
        def __init__(self, content, headers, status_code=200, request_headers=None):
            self._content = content
            self.headers = headers
            self.status_code = status_code
            self.request = type('R', (), {'headers': request_headers or {}})()

        @property
        def content(self):
            return self._content

        def json(self):
            return json.loads(self._content.decode('utf-8'))

    samples = [
        DummyResponse(json.dumps({'ok': True, 'items': [1, 2, 3]}).encode('utf-8'), {'Content-Type': 'application/json; charset=utf-8'}),
        DummyResponse(b"<root><a>1</a><b>two</b></root>", {'Content-Type': 'application/xml'}),
        DummyResponse(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n...', {'Content-Type': 'application/pdf'}, status_code=200),
        DummyResponse(b'a,b,c\n1,2,3', {'Content-Type': 'text/csv'}),
        DummyResponse(b'plain text response', {'Content-Type': 'text/plain'})
    ]

    for i, sample in enumerate(samples, start=1):
        proc = process_response(sample)
        metadata = {'generated_at': time.ctime(), 'api_endpoint': f'simulated://sample/{i}', 'method': 'SIM'}
        request_info = {'headers': {}, 'body_summary': None}
        response_info = {'status_code': sample.status_code, 'headers': sample.headers, 'detected_type': proc.get('type'), 'summary': proc.get('summary'), 'artifact': proc.get('artifact')}
        out_pdf = os.path.join(out_dir, f"sim_report_{i}.pdf")
        generate_api_report_pdf(out_pdf, metadata, request_info, response_info, notes=proc.get('notes'))
        print(f"Gerado: {out_pdf} (tipo {proc.get('type')})")


def _cli():
    parser = argparse.ArgumentParser(description='BizDocs_Integrator CLI - gerar relatórios de API')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--simulate', action='store_true', help='Gerar relatórios de simulação (sem chamadas externas)')
    group.add_argument('--url', help='URL da API a chamar (quando não usa um método nomeado)')
    parser.add_argument('--method', default='GET', help='HTTP method a usar (GET/POST/PUT/DELETE)')
    parser.add_argument('--payload-file', help='Ficheiro JSON com payload para o body (usado em POST/PUT)')
    parser.add_argument('--payload', help='Payload JSON inline (ex: "{\\"a\\":1}")')
    parser.add_argument('--method-name', help='Nome do método definido em methods.json ou na Postman collection')
    default_postman = str(pathlib.Path(__file__).parent / 'BIZDOCS - API.postman_collection.json')
    parser.add_argument('--methods-file', default=default_postman, help='Ficheiro JSON com métodos nomeados ou Postman collection')
    parser.add_argument('--var', action='append', help='Substituições para placeholders {{name}} no URL/payload, no formato name=value. Pode repetir.')
    parser.add_argument('--out-dir', default='reports', help='Diretoria onde os PDFs serão gerados')
    parser.add_argument('--no-token', action='store_true', help='Não usar authorization header (útil para endpoints públicos ou testes)')
    args = parser.parse_args()

    if args.simulate:
        simulate_responses(out_dir=args.out_dir)
        return

    url = args.url
    method = args.method.upper() if args.method else 'GET'
    payload = None

    if args.method_name:
        # Carregar methods.json ou Postman collection
        try:
            with open(args.methods_file, 'r', encoding='utf-8') as f:
                methods_blob = json.load(f)
        except FileNotFoundError:
            raise SystemExit(f"Ficheiro de métodos não encontrado: {args.methods_file}")

        # Detectar se é uma Postman collection (tem chave 'item')
        if isinstance(methods_blob, dict) and 'item' in methods_blob:
            try:
                url, method, payload = _load_method_from_postman(args.methods_file, args.method_name)
            except KeyError as e:
                raise SystemExit(str(e))
        else:
            entry = methods_blob.get(args.method_name)
            if not entry:
                raise SystemExit(f"Método '{args.method_name}' não encontrado em {args.methods_file}")
            url = entry.get('url')
            method = entry.get('method', method).upper()
            payload = entry.get('payload_template')

    # Payload do ficheiro tem prioridade sobre template
    if args.payload_file:
        with open(args.payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
    elif args.payload:
        try:
            payload = json.loads(args.payload)
        except Exception as e:
            raise SystemExit(f'Payload JSON inválido: {e}')

    if not url:
        raise SystemExit('Tem de fornecer --url ou --method-name ou usar --simulate')

    # Aplicar placeholders {{name}} usando vars CLI ou variáveis de ambiente
    def apply_placeholders(s: str, vars_map: dict):
        if not isinstance(s, str):
            return s
        out = s
        import re
        for m in re.findall(r"\{\{([^}]+)\}\}", s):
            key = m.strip()
            if key in vars_map:
                out = out.replace('{{'+key+'}}', vars_map[key])
            else:
                env = os.environ.get(key)
                if env is not None:
                    out = out.replace('{{'+key+'}}', env)
        return out

    # default placeholder values: always-constant VAT id + api host inferred from auth_manager
    default_vars = {}
    # VAT id constant provided by user
    default_vars['api-bzd-companyvatid'] = 'PT504419811'
    # infer api-bzd base URL from auth_manager.TOKEN_URL if possible
    try:
        parsed = urllib.parse.urlparse(getattr(auth_manager, 'TOKEN_URL', '') or '')
        if parsed.scheme and parsed.netloc:
            default_vars['api-bzd'] = f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        pass

    vars_map = default_vars.copy()
    if args.var:
        for pair in args.var:
            if '=' in pair:
                k, v = pair.split('=', 1)
                vars_map[k] = v

    # apply to url and payload if needed
    url = apply_placeholders(url, vars_map) if url else url
    if isinstance(payload, str):
        payload = apply_placeholders(payload, vars_map)
        try:
            payload = json.loads(payload)
        except Exception:
            pass
    elif isinstance(payload, dict):
        # naive recursive replace in strings
        def replace_in_obj(obj):
            if isinstance(obj, str):
                return apply_placeholders(obj, vars_map)
            if isinstance(obj, dict):
                return {k: replace_in_obj(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [replace_in_obj(i) for i in obj]
            return obj
        payload = replace_in_obj(payload)

    # if url still contains placeholders, abort with helpful message
    if url and '{{' in url and '}}' in url:
        raise SystemExit(f'URL ainda contém placeholders não resolvidos: {url}. Use --var name=value ou defina variáveis de ambiente correspondentes.')

    if args.no_token:
        import requests as _req
        headers = {}
        if method == 'GET':
            resp = _req.get(url, headers=headers)
        else:
            headers['Content-Type'] = 'application/json'
            resp = _req.request(method, url, headers=headers, json=payload)
        proc = process_response(resp)
        metadata = {'generated_at': time.ctime(), 'api_endpoint': url, 'method': method}
        request_info = {'headers': dict(resp.request.headers) if resp.request is not None else {}, 'body_summary': (json.dumps(payload, ensure_ascii=False, indent=2) if payload else None)}
        response_info = {'status_code': resp.status_code, 'headers': dict(resp.headers), 'detected_type': proc.get('type'), 'summary': proc.get('summary'), 'artifact': proc.get('artifact')}
        out_pdf = os.path.join(args.out_dir, f"report_cli_{int(time.time())}.pdf")
        generate_api_report_pdf(out_pdf, metadata, request_info, response_info, notes=proc.get('notes'))
        print(out_pdf)
    else:
        out = call_protected_api_and_report(url, method=method, payload=payload, out_dir=args.out_dir)
        print(out)


if __name__ == '__main__':
    _cli()