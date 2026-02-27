* Função VFP para executar Python e exibir resultados em browse list
* Se Python retornar OK, lê JSON e mostra os dados
json_listing(fo.no)
Function json_listing(ncont)
	Local lcCommand, lcResult, loShell, lcJsonFile, lcJsonText, lSuccess

	* Usar o batch script para executar
	lcCommand = "c:\trigenius\BizDocs_Integrator\run.bat"
	lSuccess = .T.

	Try
		loShell = Createobject("WScript.Shell")
		* Usar Run em vez de Exec para evitar bloqueios
		loShell.Run(lcCommand, 0, .F.)  && 0=hidden, .T.=wait until finish

		* Dar tempo ao .exe de criar os ficheiros JSON
		Inkey(3)  && espera 3 segundos

		* Se chegou aqui, foi OK - obter último ficheiro JSON na pasta reports
		lcJsonFile = GET_LATEST_JSON_FILE()
		If Empty(lcJsonFile)
			Messagebox("Nenhum ficheiro JSON encontrado na pasta reports (c:\Projetos\BizDocs_Integrator\reports)", 16, "Erro")
			lSuccess = .F.
		Endif

		If lSuccess
			* Ler ficheiro
			lcJsonText = Filetostr(lcJsonFile)

			* Criar cursor e popular
			CREATE_CURSOR(lcJsonText)

			* Extrair dados do JSON e inserir no cursor
			Select temp_json
			If READ_JSON_AND_INSERT(lcJsonText,"temp_json","items")
				* Mostrar browse list
				SHOW_BROWSE()
			Else
				msg("Erro a ler json e inserir dados no cursor!")
			Endif
		Endif

	Catch To loError
		Messagebox("Erro: " + loError.Message, 16, "Erro")
		lSuccess = .F.
	Endtry

	Return lSuccess
Endfunc


* Função para obter o ficheiro JSON mais recente da pasta reports
Function GET_LATEST_JSON_FILE()
	Local lcReportsDir, laFiles[1], nCount, nI, lcNewest

	lcReportsDir = "c:\Trigenius\BizDocs_Integrator\reports"
	lcNewest = ""

	* Procurar todos os ficheiros JSON
	nCount = Adir(laFiles, lcReportsDir + "\in_accounting_items*.json")

	If nCount > 0
		* Último ficheiro (ordenado alfabeticamente, o maior nome é o mais recente)
		msg(Alltrim(laFiles[nCount, 1]))
		lcNewest = lcReportsDir + "\" + Alltrim(laFiles[nCount, 1])
	Endif

	Return lcNewest
Endfunc



* Função para criar cursor a partir do JSON
Function CREATE_CURSOR(tcJsonText)
	*Criar cursor
	Create Cursor temp_json (;
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
Endfunc

Function READ_JSON_AND_INSERT(tcJsonText, tcCursorName, tcArrayName)
	************************************************************************
	* Converte um JsonArray numa tabela/cursor, detectando propriedades
	* mesmo quando não existem em todos os elementos.
	************************************************************************

	Lparameters ooJsonArray, cNomeCursor, itemName
	ooJsonArray=tcJsonText
	cNomeCursor=tcCursorName
	itemName=tcArrayName
	Local loJson, oJsonArray, F, z, g
	Local a_AllFields[1], nFields, aTmp[1], nTmp
	Local cFieldName, cCampoEval, oVal, cType, nLen
	Local cCreateCommand, cCreateCampo

	* Decodificar apenas uma vez
	loJson = JSONDECODE(ooJsonArray)

	* Fechar cursor se existir
	If Used(cNomeCursor)
		fecha(cNomeCursor)
	Endif

	* Extrair elemento interno ou usar raiz
	If Vartype(itemName) = "C" And !Empty(itemName)
		oJsonArray = loJson.&itemName.
	Else
		oJsonArray = loJson
	Endif

	* Validar se é JsonArray
	If Vartype(oJsonArray) = "O" And Lower(oJsonArray.Class) = "jsonarray"

		If oJsonArray.Count = 0
			Return .F.
		Endif

		********************************************************************
		* 1) RECOLHER TODAS AS PROPRIEDADES DE TODOS OS ELEMENTOS DO ARRAY
		********************************************************************

		nFields = 0
		Dimension a_AllFields[1]

		For z = 1 To oJsonArray.Count
			nTmp = Amembers(aTmp, oJsonArray.Item(z))
			For F = 1 To nTmp
				If Ascan(a_AllFields, aTmp[F]) = 0
					nFields = nFields + 1
					Dimension a_AllFields[nFields]
					a_AllFields[nFields] = aTmp[F]
				Endif
			Next
		Next

		* Agora temos TODOS os campos possíveis no array
		Dimension a_JsonEstrutura[nFields]
		Acopy(a_AllFields, a_JsonEstrutura)
		nCols = nFields

		********************************************************************
		* 2) CRIAR COMANDO CREATE CURSOR DINÂMICO
		********************************************************************

		cCreateCommand = ""

		For F = 1 To nCols

			cFieldName = a_JsonEstrutura[F]
			If Len(cFieldName) > 15
				cFieldNameCursor = "coluna"+astr(F)
			Else
				cFieldNameCursor = cFieldName
			Endif


			**if Type(oJsonArray.Item(1).&cFieldName) <> "U"
			**cCampoEval = "oJsonArray.Item(1)." + cFieldName
			**else
			**
			**endif

			**cType = Type(cCampoEval)
			**oVal  = Evaluate(cCampoEval)

			cCampoEval = ""  && inicializar

			For z = 1 To oJsonArray.Count
				If Pemstatus(oJsonArray.Item(z), cFieldName, 5)  && verifica se o campo existe
					cCampoEval = "oJsonArray.Item("+Transform(z)+")." + cFieldName
					Exit  && sai do loop, encontramos um elemento com o campo
				Endif
			Next

			If Empty(cCampoEval)
				* Nenhum elemento tem este campo
				cType = "C"  && ou outro tipo default
				oVal  = ""
			Else
				cType = Type(cCampoEval)
				oVal  = Evaluate(cCampoEval)
			Endif

			* Detectar datetime ISO
			If cType = "C"
				Local xTry
				xTry = Ctot(Transform(oVal, "@R^9999-99-99T99:99:99"))
				If !Empty(xTry)
					cType = "T"
				Endif
			Endif

			Do Case

				Case cType = "C"
					* Encontrar maior tamanho em todos os elementos
					nLen = 1
					For z = 1 To oJsonArray.Count
						If Pemstatus(oJsonArray.Item(z), cFieldName, 5)  && verifica se o campo existe
							cCampoEval = "oJsonArray.Item(z)." + cFieldName
							nLen = Max(nLen, Len(Nvl(Evaluate(cCampoEval), "")))
						Endif
					Next
					cCreateCampo = cFieldNameCursor + " C(" + Transform(nLen) + ")"

				Case cType = "D" Or cType = "T"
					cCreateCampo = cFieldNameCursor + " D"

				Case cType = "L"
					cCreateCampo = cFieldNameCursor + " L"

				Case cType = "N"
					cCreateCampo = cFieldNameCursor + " N(15,5)"

				Otherwise
					* Não suportado
					cCreateCampo = ""
			Endcase

			If !Empty(cCreateCampo)
				If Empty(cCreateCommand)
					cCreateCommand = "CREATE CURSOR "+cNomeCursor+" ("
				Else
					cCreateCommand = cCreateCommand + ", "
				Endif
				cCreateCommand = cCreateCommand + cCreateCampo
			Endif

		Next

		cCreateCommand = cCreateCommand + ")"

		********************************************************************
		* 3) CRIAR O CURSOR
		********************************************************************

		&cCreateCommand.


		********************************************************************
		* 4) PREENCHER O CURSOR COM OS DADOS DO JSON
		********************************************************************

		For g = 1 To oJsonArray.Count

			Select (cNomeCursor)
			Append Blank

			For F = 1 To nCols

				cFieldName = a_JsonEstrutura[F]
				If Len(cFieldName) > 15
					cFieldNameCursor = "coluna"+astr(F)
				Else
					cFieldNameCursor = cFieldName
				Endif

				* Existem campos que podem não existir neste elemento
				If Type(cNomeCursor+"."+cFieldNameCursor) <> "U"
					If Pemstatus(oJsonArray.Item(g), cFieldName, 5)  && verifica se o campo existe
						cCampoEval = "oJsonArray.Item(g)." + cFieldName
						oVal = Evaluate(cCampoEval)
						If !Isnull(oVal)
							* Converter datetime ISO ? DATE
							If Type(cNomeCursor+"."+cFieldNameCursor) = "D"
								oVal = Ttod(Ctot(oVal))
							Endif
							* Preencher se não for objeto
							If Type(cNomeCursor+"."+cFieldNameCursor) <> "O"
								Replace (cFieldNameCursor) With oVal In (cNomeCursor)
							Endif
						Endif
					Endif
				Endif

			Next

		Next

		Return .T.

	Endif

	Return .F.

Endfunc


* Função para mostrar browse list
Function SHOW_BROWSE()
	Local m.ntotcampos, m.ncampo
	Local list_tit, list_cam, list_tam, list_pic, list_ronly

	= CursorSetProp('Buffering', 5, 'temp_json')

	m.ntotcampos = 7
	m.ncampo = 1
	Declare list_tit(m.ntotcampos), list_cam(m.ntotcampos), list_tam(m.ntotcampos), ;
		list_pic(m.ntotcampos), list_ronly(m.ntotcampos)

	list_tit(m.ncampo) = "Documento"
	list_cam(m.ncampo) = "temp_json.documentNumber"
	list_ronly(m.ncampo) = .T.
	list_pic(m.ncampo) = ""
	list_tam(m.ncampo) = 8*40
	m.ncampo = m.ncampo + 1

	list_tit(m.ncampo) = "Nome"
	list_cam(m.ncampo) = "temp_json.documentName"
	list_ronly(m.ncampo) = .T.
	list_pic(m.ncampo) = ""
	list_tam(m.ncampo) = 8*60
	m.ncampo = m.ncampo + 1

	list_tit(m.ncampo) = "Data"
	list_cam(m.ncampo) = "temp_json.documentDate"
	list_ronly(m.ncampo) = .T.
	list_pic(m.ncampo) = ""
	list_tam(m.ncampo) = 8*40
	m.ncampo = m.ncampo + 1

	list_tit(m.ncampo) = "Valor"
	list_cam(m.ncampo) = "temp_json.documentTotalAmount"
	list_ronly(m.ncampo) = .T.
	list_pic(m.ncampo) = "9999999.99"
	list_tam(m.ncampo) = 8*40
	m.ncampo = m.ncampo + 1

	list_tit(m.ncampo) = "Estado"
	list_cam(m.ncampo) = "temp_json.documentStatus"
	list_ronly(m.ncampo) = .T.
	list_pic(m.ncampo) = ""
	list_tam(m.ncampo) = 8*40
	m.ncampo = m.ncampo + 1

	list_tit(m.ncampo) = "NIF Fornecedor"
	list_cam(m.ncampo) = "temp_json.documentVendorVatId"
	list_ronly(m.ncampo) = .T.
	list_pic(m.ncampo) = ""
	list_tam(m.ncampo) = 8*40
	m.ncampo = m.ncampo + 1

	list_tit(m.ncampo) = "ID"
	list_cam(m.ncampo) = "temp_json.documentId"
	list_ronly(m.ncampo) = .T.
	list_pic(m.ncampo) = ""
	list_tam(m.ncampo) = 8*50

	m.Escolheu = .F.

	browlist('Documentos BizDocs', 'temp_json', 'temp_json', .T., .F., .F., .T., .F., '', .T.)

	If m.Escolheu = .F.
		Return
	Endif
Endfunc
