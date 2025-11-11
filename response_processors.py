"""Módulo para processar respostas HTTP por tipo de conteúdo.

Exporta `process_response(response)` que detecta o tipo da resposta e chama
o processador adequado. Cada processador devolve um dicionário com chaves:
 - type: string identificando o tipo detectado
 - summary: texto resumido para inclusão em relatórios
 - artifact: opcional, caminho para ficheiro guardado (ex.: PDF ou binário)
 - notes: opcional, string com observações
"""

import os
import json
import time
import xml.etree.ElementTree as ET
import io


def _save_binary(content_bytes, ext):
    os.makedirs('artifacts', exist_ok=True)
    filename = f"artifacts/artifact_{int(time.time()*1000)}.{ext}"
    with open(filename, 'wb') as f:
        f.write(content_bytes)
    return filename


def _process_json(response, content_bytes):
    try:
        if hasattr(response, 'json'):
            data = response.json()
        else:
            data = json.loads(content_bytes.decode('utf-8'))
        summary = ''
        if isinstance(data, dict):
            summary = f"JSON object with keys: {', '.join(list(data.keys())[:10])}"
        elif isinstance(data, list):
            summary = f"JSON array of length {len(data)}"
        else:
            summary = f"JSON value of type {type(data).__name__}"
        return {'type': 'json', 'summary': summary, 'artifact': None}
    except Exception as e:
        return {'type': 'json', 'summary': f'Failed to parse JSON: {e}', 'artifact': None, 'notes': str(e)}


def _process_xml(response, content_bytes):
    try:
        root = ET.fromstring(content_bytes)
        tags = [child.tag for child in list(root)[:10]]
        summary = f"XML root: {root.tag}; child tags: {', '.join(tags)}"
        return {'type': 'xml', 'summary': summary, 'artifact': None}
    except Exception as e:
        return {'type': 'xml', 'summary': f'Failed to parse XML: {e}', 'artifact': None, 'notes': str(e)}


def _process_pdf(response, content_bytes):
    # Guarda o PDF recebido num ficheiro e devolve o caminho
    try:
        path = _save_binary(content_bytes, 'pdf')
        return {'type': 'pdf', 'summary': f'PDF saved to {path}', 'artifact': path}
    except Exception as e:
        return {'type': 'pdf', 'summary': f'Failed to save PDF: {e}', 'artifact': None, 'notes': str(e)}


def _process_csv(response, content_bytes):
    try:
        text = content_bytes.decode('utf-8', errors='replace')
        first_line = text.splitlines()[0] if text.splitlines() else ''
        summary = f'CSV preview header: {first_line}'
        path = _save_binary(content_bytes, 'csv')
        return {'type': 'csv', 'summary': summary, 'artifact': path}
    except Exception as e:
        return {'type': 'csv', 'summary': f'Failed to process CSV: {e}', 'artifact': None, 'notes': str(e)}


def _process_text(response, content_bytes):
    try:
        text = content_bytes.decode('utf-8', errors='replace')
        summary = text[:500].replace('\n', ' ')
        return {'type': 'text', 'summary': summary, 'artifact': None}
    except Exception as e:
        return {'type': 'text', 'summary': f'Failed to decode text: {e}', 'artifact': None, 'notes': str(e)}


def _process_unknown(response, content_bytes):
    # Tenta JSON, depois grava como binário
    try:
        return _process_json(response, content_bytes)
    except Exception:
        path = _save_binary(content_bytes, 'bin')
        return {'type': 'binary', 'summary': f'Binary data saved to {path}', 'artifact': path}


def process_response(response):
    """Detecta o tipo de resposta e chama o processador adequado.

    `response` pode ser um `requests.Response` ou um objecto com `.headers` e `.content`.
    Retorna um dicionário com chaves descritas no topo do ficheiro.
    """
    headers = getattr(response, 'headers', {}) or {}
    content_type = headers.get('Content-Type', headers.get('content-type', '')).lower()
    # Extrair bytes
    content_bytes = None
    if hasattr(response, 'content'):
        try:
            content_bytes = response.content
        except Exception:
            # objectos de simulação podem ter _content
            content_bytes = getattr(response, '_content', None)
    else:
        content_bytes = getattr(response, '_content', b'')

    if content_bytes is None:
        content_bytes = b''

    # Roteamento básico por content-type
    if 'application/json' in content_type or content_type.startswith('application/ld+json'):
        return _process_json(response, content_bytes)
    if 'application/xml' in content_type or content_type.endswith('+xml') or content_type == 'text/xml':
        return _process_xml(response, content_bytes)
    if 'application/pdf' in content_type:
        return _process_pdf(response, content_bytes)
    if 'text/csv' in content_type or content_type.endswith('+csv') or content_type == 'text/csv':
        return _process_csv(response, content_bytes)
    if content_type.startswith('text/'):
        return _process_text(response, content_bytes)

    # Fallback
    return _process_unknown(response, content_bytes)
