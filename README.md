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
