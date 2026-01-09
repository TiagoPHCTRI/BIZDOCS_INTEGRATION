* Programa VFP para ler JSON de um ficheiro e criar uma listagem
* Inspirado em exemplos PHC: carregar dados num cursor e exibir num grid de formulário
* Lê o JSON gerado pelo script Python (C:\temp\in_accounting.json)

LOCAL lcFileName, lcJsonText, lnI, loItem

* Definir o nome do ficheiro JSON (gerado pelo Python)
lcFileName = "C:\temp\in_accounting.json"

* Verificar se o ficheiro existe
IF NOT FILE(lcFileName)
    MESSAGEBOX("Ficheiro JSON não encontrado: " + lcFileName)
    RETURN
ENDIF

* Ler o conteúdo do ficheiro
lcJsonText = FILETOSTR(lcFileName)

* Criar uma tabela temporária com os campos do JSON
CREATE CURSOR temp_json (;
    journalGroupName C(50), ;
    accountancyYear N(4), ;
    accountancyMonth N(2), ;
    costCenter C(50), ;
    documentDate C(10), ;
    documentNumber C(50), ;
    documentVendorVatId C(20), ;
    documentCustomerVatId C(20), ;
    documentTotalAmount N(10,2), ;
    documentStatus C(20), ;
    updatedOn C(20), ;
    documentId C(50), ;
    createdOn C(20), ;
    documentName C(100) ;
)

* Parsing simples (remover chaves e dividir por objetos)
lcJsonText = STRTRAN(lcJsonText, '[', '')
lcJsonText = STRTRAN(lcJsonText, ']', '')
lcJsonText = STRTRAN(lcJsonText, '{', '')
lcJsonText = STRTRAN(lcJsonText, '}', '')
lcJsonText = STRTRAN(lcJsonText, '"', '')

* Assumir que "items:" precede a lista; remover prefixos
lnPos = AT('items:', lcJsonText)
IF lnPos > 0
    lcJsonText = SUBSTR(lcJsonText, lnPos + 6)
ENDIF

* Dividir por objetos (vírgula entre objetos)
LOCAL laObjects
laObjects = ALINES(laObjects, lcJsonText, .T., ',')

FOR lnI = 1 TO ALEN(laObjects)
    loItem = laObjects[lnI]
    * Extrair valores para cada campo
    LOCAL lcJournalGroupName, lnAccountancyYear, lnAccountancyMonth, lcCostCenter, ;
          lcDocumentDate, lcDocumentNumber, lcDocumentVendorVatId, lcDocumentCustomerVatId, ;
          lnDocumentTotalAmount, lcDocumentStatus, lcUpdatedOn, lcDocumentId, lcCreatedOn, lcDocumentName
    
    lcJournalGroupName = STREXTRACT(loItem, 'journalGroupName:', ',', 1)
    lnAccountancyYear = VAL(STREXTRACT(loItem, 'accountancyYear:', ',', 1))
    lnAccountancyMonth = VAL(STREXTRACT(loItem, 'accountancyMonth:', ',', 1))
    lcCostCenter = STREXTRACT(loItem, 'costCenter:', ',', 1)
    lcDocumentDate = STREXTRACT(loItem, 'documentDate:', ',', 1)
    lcDocumentNumber = STREXTRACT(loItem, 'documentNumber:', ',', 1)
    lcDocumentVendorVatId = STREXTRACT(loItem, 'documentVendorVatId:', ',', 1)
    lcDocumentCustomerVatId = STREXTRACT(loItem, 'documentCustomerVatId:', ',', 1)
    lnDocumentTotalAmount = VAL(STREXTRACT(loItem, 'documentTotalAmount:', ',', 1))
    lcDocumentStatus = STREXTRACT(loItem, 'documentStatus:', ',', 1)
    lcUpdatedOn = STREXTRACT(loItem, 'updatedOn:', ',', 1)
    lcDocumentId = STREXTRACT(loItem, 'documentId:', ',', 1)
    lcCreatedOn = STREXTRACT(loItem, 'createdOn:', ',', 1)
    lcDocumentName = STREXTRACT(loItem, 'documentName:', '', 1)
    
    * Inserir na tabela temporária
    INSERT INTO temp_json VALUES (;
        lcJournalGroupName, lnAccountancyYear, lnAccountancyMonth, lcCostCenter, ;
        lcDocumentDate, lcDocumentNumber, lcDocumentVendorVatId, lcDocumentCustomerVatId, ;
        lnDocumentTotalAmount, lcDocumentStatus, lcUpdatedOn, lcDocumentId, lcCreatedOn, lcDocumentName ;
    )
ENDFOR

* Criar um formulário simples com grid, estilo PHC
LOCAL loForm
loForm = CREATEOBJECT('Form')
loForm.Caption = 'Listagem de Documentos - BizDocs'
loForm.Width = 1200
loForm.Height = 600

* Adicionar grid ao formulário
LOCAL loGrid
loGrid = CREATEOBJECT('Grid')
loGrid.Width = loForm.Width - 20
loGrid.Height = loForm.Height - 60
loGrid.Top = 10
loGrid.Left = 10
loGrid.RecordSource = 'temp_json'
loGrid.ReadOnly = .T.
loGrid.AllowAddNew = .F.
loGrid.AllowRowSizing = .F.
loGrid.AllowColumnSizing = .T.

* Configurar colunas do grid
loGrid.ColumnCount = 14
loGrid.Columns[1].Header1.Caption = 'Grupo Diário'
loGrid.Columns[1].Width = 100
loGrid.Columns[2].Header1.Caption = 'Ano'
loGrid.Columns[2].Width = 50
loGrid.Columns[3].Header1.Caption = 'Mês'
loGrid.Columns[3].Width = 50
loGrid.Columns[4].Header1.Caption = 'Centro Custo'
loGrid.Columns[4].Width = 100
loGrid.Columns[5].Header1.Caption = 'Data Doc'
loGrid.Columns[5].Width = 80
loGrid.Columns[6].Header1.Caption = 'Número Doc'
loGrid.Columns[6].Width = 100
loGrid.Columns[7].Header1.Caption = 'NIF Fornecedor'
loGrid.Columns[7].Width = 100
loGrid.Columns[8].Header1.Caption = 'NIF Cliente'
loGrid.Columns[8].Width = 100
loGrid.Columns[9].Header1.Caption = 'Total'
loGrid.Columns[9].Width = 80
loGrid.Columns[10].Header1.Caption = 'Estado'
loGrid.Columns[10].Width = 80
loGrid.Columns[11].Header1.Caption = 'Atualizado'
loGrid.Columns[11].Width = 100
loGrid.Columns[12].Header1.Caption = 'ID Doc'
loGrid.Columns[12].Width = 150
loGrid.Columns[13].Header1.Caption = 'Criado'
loGrid.Columns[13].Width = 100
loGrid.Columns[14].Header1.Caption = 'Nome Doc'
loGrid.Columns[14].Width = 150

* Adicionar botão fechar
LOCAL loBtnClose
loBtnClose = CREATEOBJECT('CommandButton')
loBtnClose.Caption = 'Fechar'
loBtnClose.Top = loForm.Height - 40
loBtnClose.Left = loForm.Width - 100
loBtnClose.Click = 'loForm.Release()'

* Adicionar controles ao formulário
loForm.AddObject('Grid1', 'Grid')
loForm.Grid1 = loGrid
loForm.AddObject('BtnClose', 'CommandButton')
loForm.BtnClose = loBtnClose

* Mostrar formulário
loForm.Show()

* Limpar cursor após fechar
loForm.Release()
USE IN temp_json
DELETE FILE "temp_json.dbf"