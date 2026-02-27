# BizDocs Integrator

Integração Python + VFP para extrair documentos do BizDocs API.

## Requisitos

- Python 3.7+
- Ficheiro de autenticação configurado (`auth_manager.py`)
- Pasta `reports/` será criada automaticamente

## Como usar

### Opção 1: Executar o script batch (Windows)

```bash
run.bat
```

Este script:
1. Executa `dist\main.exe`
2. Guarda os ficheiros JSON em `reports\`
3. Mostra mensagem de conclusão

### Opção 2: Executar direto via Python (linha de comando)

```bash
python main.py
```

### Opção 3: Usar no VFP

```foxpro
json_listing('PT504419811')  && Passa VAT ID opcional
```

## Ficheiros importantes

- `main.py` - Script principal Python
- `auth_manager.py` - Autenticação e gestão de tokens
- `json_listing.prg` - Integração VFP (consulta e exibe dados)
- `dist/main.exe` - Executável standalone (gerado por PyInstaller)
- `reports/` - Pasta com ficheiros JSON gerados (formato: `in_accounting_items_YYYY-MM-DD_HHMMSS.json`)

## Gerar novo executável

Se fizeres alterações ao `main.py`:

```bash
pyinstaller --onefile main.py
```

Isto cria `dist\main.exe` novamente.

## Estrutura de ficheiros

```
BizDocs_Integrator/
├── main.py
├── auth_manager.py
├── json_listing.prg
├── run.bat
├── requirements.txt
├── reports/
│   ├── in_accounting_items_2026-02-05_143045.json
│   └── ...
└── dist/
    └── main.exe
```

## Resolução de problemas

- **"main.exe não encontrado"**: Execute `pyinstaller --onefile main.py`
- **Erro de autenticação**: Verificar credenciais em `auth_manager.py`
- **Pasta reports vazia**: Verificar se a API retorna dados

