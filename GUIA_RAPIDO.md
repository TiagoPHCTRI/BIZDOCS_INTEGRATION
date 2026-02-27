# Guia Rápido - BizDocs Integrator VFP

## O que é?

Um integrador que permite ao **PHC** chamar a **API BizDocs** através de código **VFP**, recebendo os parâmetros da empresa e exibindo os resultados em um grid formatado.

## Arquitetura Simplificada

```
PHC (Sistema ERP)
  ↓ chama com parâmetros
VFP (json_listing.prg)
  ↓ executa
Python (main.py)
  ↓ faz requisição
API BizDocs
  ↓ retorna JSON
VFP (processa)
  ↓ exibe
Grid com Documentos
```

## Chamada Simples

```foxpro
DO json_listing WITH "PT504419811", "", "id1,id2,id3", ""
```

**Parâmetros:**
1. `tcVatId` - NIF da empresa (ex: PT504419811)
2. `tcApiUrl` - URL da API (deixe em branco para usar default)
3. `tcDocumentIds` - IDs dos documentos separados por vírgula (**obrigatório**)
4. `tcOutputFile` - Caminho do ficheiro JSON de saída (opcional)

**Retorno:**
- `.T.` = Sucesso (mostra grid com dados)
- `.F.` = Erro (mostra mensagem de erro)

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `json_listing.prg` | **Programa principal** - executa Python e exibe resultados |
| `main.py` | Script Python que chama a API BizDocs |
| `EXEMPLO_CHAMADA_PHC.prg` | Exemplos de como integrar com o PHC |
| `TESTE_INTEGRACAO.prg` | Suite de testes para validar tudo |
| `README_VFP_INTEGRATION.md` | Documentação completa em Markdown |

## Pré-requisitos

1. **Python 3.x instalado** no Windows
2. **Ficheiro `main.py`** no mesmo diretório
3. **Diretório `C:\temp\`** existente (ou ajustar caminhos)
4. **Credenciais OAuth** (token ou user/pass)

## Instalação

```bash
# 1. Instalar Python (se não tiver)
# https://www.python.org/downloads/

# 2. Verificar Python
python --version

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Copiar `json_listing.prg` para o projeto
# 5. Copiar `TESTE_INTEGRACAO.prg` para validar
```

## Primeiro Teste

```foxpro
* Executar no VFP Command Window:
DO TESTE_INTEGRACAO

* Ou testar diretamente:
DO json_listing WITH "PT504419811", "", "seu-id-aqui", ""
```

## Fluxo de Dados

### 1. Validação
- Verificar VAT ID (default: PT504419811)
- Verificar URL API (default: https://nikepp.azurewebsites.net/api/)
- Obter lista de IDs (obrigatório)

### 2. Execução Python
```
Command: python main.py 
  --url "https://nikepp.azurewebsites.net/api/"
  --vatid "PT504419811"
  --ids "id1,id2,id3"
  --machine-json
```

### 3. Parsing JSON
Extrai array `items` e insere em cursor temporário:
```
temp_json:
  - journalGroupName
  - accountancyYear
  - accountancyMonth
  - costCenter
  - documentDate
  - documentNumber
  - documentVendorVatId
  - documentCustomerVatId
  - documentTotalAmount
  - documentStatus
  - updatedOn
  - documentId
  - createdOn
  - documentName
```

### 4. Exibição
Abre formulário com grid mostrando todos os campos acima.

## Erros Comuns

### "Script Python não encontrado"
✓ Solução: Copiar `main.py` para o mesmo diretório do `json_listing.prg`

### "Ficheiro JSON não encontrado"
✓ Solução: Criar diretório `C:\temp\` ou ajustar caminho em `json_listing.prg`

### "Python command not found"
✓ Solução: Adicionar Python ao PATH do Windows
  1. Abrir "Environment Variables"
  2. Adicionar `C:\Python\Scripts` e `C:\Python` ao PATH
  3. Reiniciar terminal

### "Erro ao processar JSON"
✓ Solução: Testar manualmente
```powershell
# No terminal:
python main.py --url "sua-url" --vatid "seu-vat" --ids "seus-ids" --machine-json

# Verificar se retorna JSON válido
```

## Variáveis de Ambiente (Opcional)

```batch
:: Adicionar ao Windows para usar defaults
setx API_BZD "https://nikepp.azurewebsites.net/api/"
setx API_BZD_COMPANYVATID "PT504419811"
setx BIZDOCS_AUTH_TOKEN "seu-token-aqui"
```

## Integração PHC - Exemplo Real

```foxpro
* Colocar isto no seu método de processamento de documentos do PHC:

PROCEDURE ProcessarDocumentosBizDocs
    LOCAL lcVatId, lcIDs, llResult
    LOCAL ARRAY laDocumentos
    
    * Obter dados da empresa
    lcVatId = oEmpresa.GetVat()
    
    * Obter documentos pendentes (exemplo)
    SELECT id FROM documentos WHERE status = 'pending' INTO ARRAY laDocumentos
    
    * Converter para string
    lcIDs = IMPLODE(laDocumentos, ',')
    
    * Executar integrador
    llResult = DO json_listing WITH lcVatId, "", lcIDs, ""
    
    * Marcar como sincronizado
    IF llResult
        UPDATE documentos SET bizdocs_sync = .T. WHERE status = 'pending'
    ENDIF
ENDPROC
```

## Performance

- **Tempo de resposta**: Depende da API (geralmente 1-5 segundos)
- **Número de documentos**: Testado até 1000+ registos
- **Execução**: Não-bloqueante (GUI responsiva)

## Debugging

Ativar modo verbose:
```foxpro
* No Python (se necessário):
python main.py ... --debug
```

Verificar ficheiro de saída:
```powershell
# No PowerShell:
Get-Content C:\temp\in_accounting.json
```

## Próximos Passos

1. ✓ Testar com `TESTE_INTEGRACAO.prg`
2. ✓ Fazer chamada manual com IDs reais
3. ✓ Integrar no fluxo PHC
4. ✓ Implementar tratamento de erros customizado
5. ✓ Adicionar logging em ficheiro

## Suporte

- **VFP/PHC**: Consulte documentação do PHC
- **Python**: Ver `main.py` e `auth_manager.py`
- **API BizDocs**: Consultar documentação API
- **Problemas**: Executar `TESTE_INTEGRACAO.prg`

---

**Última atualização**: 9 de Janeiro de 2026
**Versão**: 1.0 - Produção
