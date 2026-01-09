# BizDocs Integrator — InAccounting usage

This document explains how to run the included `main.py` script to call the Documents/InAccounting endpoint, where the JSON response is written, and simple ways to consume the result from Visual FoxPro (VFP).

## Overview

- `main.py` obtains an OAuth token via `auth_manager.get_access_token()` and calls the Documents/InAccounting endpoint for the configured company VAT id.
- After a successful call the script:
  - stores the parsed canonical response object in memory (`IN_ACCOUNTING_RESPONSE`),
  - stores the items list in `IN_ACCOUNTING_ITEMS`,
  - writes the canonical response JSON to `C:\temp\in_accounting.json` (UTF-8),
  - prints a pretty JSON representation to stdout.

The canonical response has the structure:

```
{
  "items": [ { ... each document object ... } ],
  "paginationKey": "string or null"
}
```

Each document object contains keys such as `documentId`, `documentNumber`, `documentName`, `documentTotalAmount`, `documentStatus`, `documentDate`, `documentVendorVatId`, `documentCustomerVatId`, etc.

## Requirements

- Python 3.8+
- `requests` package

Install requirements (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install requests
```

Make sure `auth_manager.py` is configured with valid client/user credentials for the token endpoint.

## Running the script

Typical command (PowerShell):

```powershell
python c:\Projetos\BizDocs_Integrator\main.py --url "https://nikepp.azurewebsites.net/api/" --vatid PT504419811 --run-inaccounting --debug
```

- `--run-inaccounting` triggers the InAccounting call (the script always obtains/refreshes the token).
- `--debug` prints request/response debugging blocks useful to compare with Postman.
- `--machine-json` prints a single-line machine-friendly JSON summary instead of pretty-printing.

After the run the canonical JSON will be available at:

```
C:\temp\in_accounting.json
```

You can also capture stdout directly into a file:

```powershell
python c:\Projetos\BizDocs_Integrator\main.py --url "https://nikepp.azurewebsites.net/api/" --vatid PT504419811 --run-inaccounting > C:\temp\in_accounting_stdout.json
```

## Consuming from Visual FoxPro (VFP)

Two recommended approaches:

- Option A (recommended): Have VFP read the saved file `C:\temp\in_accounting.json` after the script runs.
  1. Use `FileToStr("C:\temp\in_accounting.json")` to get the JSON text.
  2. Parse JSON with your preferred VFP JSON library (many are available). The parsed object will contain an `items` array you can iterate.

- Option B: Run the Python script from VFP and capture stdout, then parse the JSON text returned.

Example VFP pseudo-code (high-level):

```
lcJson = FileToStr('C:\temp\in_accounting.json')
loParsed = ParseJson(lcJson)  && depends on your JSON lib
FOR EACH loItem IN loParsed.items
   ? loItem.documentId, loItem.documentNumber, loItem.documentTotalAmount
ENDFOR
```

If you don't have a JSON parser in VFP, the script also provides a CSV exporter via `export_in_accounting_csv(path)` which you can call from a Python invocation to write a CSV that VFP can easily import.

## Quick Python helpers (examples)

- Print the canonical response from the module:

```powershell
python - <<'PY'
import main, json
print(json.dumps(main.get_in_accounting_response(), ensure_ascii=False, indent=2))
PY
```

- Export CSV from Python (already implemented):

```powershell
python - <<'PY'
import main
main.call_in_accounting(vatid='PT504419811')
main.export_in_accounting_csv(r'C:\temp\in_accounting.csv')
PY
```

## Troubleshooting

- If the script fails to get a token: check `auth_manager.py` credentials and network connectivity.
- If the endpoint returns 500: run with `--debug` and compare the `--- InAccounting REQUEST ---` and `--- RESPONSE ---` blocks with the working Postman request; paste them to the developer for analysis.
- If the script cannot write to `C:\temp\in_accounting.json` ensure the folder exists and the user has write permission.

## Next steps (optional)

- Add CLI flag `--export-json <path>` to specify a different output path.
- Add `--quiet` to suppress other stdout and print only the resulting JSON.

If you want either of these, tell me which and I'll add it.
# BizDocs_Integrator — Relatórios PDF e processamento de respostas API

Este pequeno utilitário ajuda a chamar APIs protegidas (via `auth_manager`),
processar os vários tipos de resposta que pode receber e gerar um PDF de relatório
com metadados, resumo do pedido e da resposta.

O objetivo deste README é descrever o que é incluído no PDF e como estender os
processadores para novos tipos de resposta.

## O que o PDF contém

- Generated at: timestamp legível
- Endpoint: URL chamado
- Method: HTTP method usado
- Request
  - Headers (quando disponíveis)
  - Body summary (se aplicável)
- Response
  - Status code
  - Detected type (json, xml, pdf, csv, text, binary)
  - Summary: breve resumo do conteúdo (ex.: chaves JSON, primeiras linhas CSV, etc.)
  - Artifact: caminho para ficheiro guardado, se aplicável (ex.: PDF ou CSV)
- Notes: observações do processador (erros de parsing, etc.)

Os PDFs são gerados em `reports/` por defeito (ou no caminho que indicar).

## Mapeamento de tipos de resposta

O módulo `response_processors.py` implementa a deteção e processadores básicos:

- application/json -> processa e resume (chaves / tamanho)
- application/xml, text/xml -> tenta parse XML e resume tags
- application/pdf -> guarda o binário num ficheiro `.pdf`
- text/csv -> guarda o ficheiro `.csv` e mostra o cabeçalho
- text/* -> resumo do texto
- fallback -> tenta JSON, senão guarda binário

Para adicionar um novo processador, edite `response_processors.py` e acrescente
uma função `_process_<type>` e altere a lógica em `process_response` para corresponder
ao `Content-Type` desejado.

## Como usar

1. Instale as dependências (recomendado usar um virtualenv):

```
pip install -r requirements.txt
```

2. Geração de relatórios de exemplo (sem chamar APIs reais):

```
python main.py
```


3. Para chamar uma API protegida e gerar relatório:

Abra um REPL ou crie um script que importe `call_protected_api_and_report` e passe a URL.

Exemplo rápido:

```py
from main import call_protected_api_and_report
call_protected_api_and_report('https://minha.api/protected/resource')
```

## Chamar a partir do Visual FoxPro

O Visual FoxPro pode invocar comandos externos com `RUN` ou `SHELL`. Exemplo minimal:

```
* Exemplo VFP: chama o CLI Python para executar um método nomeado
CMD = 'python "C:\\Projetos\\BizDocs_Integrator\\main.py" --method-name create_order --methods-file "C:\\Projetos\\BizDocs_Integrator\\methods.json" --payload-file "C:\\temp\\order_payload.json"'
RUN /N &CMD
```

Se preferir chamar por URL diretamente:

```
CMD = 'python "C:\\Projetos\\BizDocs_Integrator\\main.py" --url "https://api.sua.org/resource" --method POST --payload-file "C:\\temp\\payload.json"'
RUN /N &CMD
```

Notas:
- Use `--no-token` se estiver a chamar endpoints públicos ou quando quiser testar sem `auth_manager`.
- Garanta que o Python e as dependências (veja `requirements.txt`) estão instalados no mesmo ambiente usado pelo comando.
- `methods.json` é um ficheiro simples onde define mapeamentos nome->endpoint/method/template. O exemplo `methods.json` no repositório mostra a estrutura.

## Campos adicionais sugeridos para o PDF

- Correlation ID (se o header `X-Correlation-ID` estiver presente)
- Tempo de resposta (latência)
- Tamanho do payload

Estes podem ser facilmente adicionados em `main.py` antes de chamar `generate_api_report_pdf`.

## Observações de segurança

- Tenha cuidado com a inclusão de segredos (tokens, passwords) nos relatórios.
  Remova ou masque valores sensíveis antes de guardar.
