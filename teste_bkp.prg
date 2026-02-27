Local loHttp, loJson, lcToken, lcUrl, lcBody, isErros

isErros = .F.
lcToken = user_ApiGetToken()
If Empty(lcToken)
	Return .F.
Endif

lcUrl = ;
	"https://nikepp.azurewebsites.net/api/Company/PT504419811/Documents/InAccounting"

lcBody = ;
	'{"documentStatus":["accountvalidation","manualentry"]}'

loHttp = Createobject("MSXML2.ServerXMLHTTP")
* timeouts em ms: resolve, connect, send, receive
loHttp.setTimeouts(3000, 3000, 5000, 5000)

Try
	loHttp.Open("POST", lcUrl, .F.)
	loHttp.setRequestHeader("Content-Type", "application/json")
	loHttp.setRequestHeader("Authorization", "Bearer " + lcToken)
	loHttp.Send(lcBody)
Catch To loErr
	Messagebox( ;
		"Não foi possível ligar ao serviço externo." + Chr(13) + ;
		"O sistema continuará a funcionar normalmente." + Chr(13) + ;
		"Detalhe: " + loErr.Message, ;
		48, "Serviço indisponível" )
	isErros = .T.
Endtry
If isErros
	Return .F.
Endif

If loHttp.Status <> 200
	Messagebox(loHttp.responseText, 16)
	Return .F.
Endif
**       msg(loHttp.responseText)
user_JsonToCursor(loHttp.responseText,"c_auxC","items")

*************************browlist****************************
If Used("c_test")
	fecha("c_test")
Endif
**duplicursor("c_auxC","c_test")
Select .F. As SEL, * From c_auxC Into Cursor c_test Readwrite



=CursorSetProp('Buffering', 5, 'c_test')

m.ntotcampos = 15
m.ncampo = 1
Declare list_tit(m.ntotcampos),list_cam(m.ntotcampos),list_tam(m.ntotcampos),list_pic(m.ntotcampos),list_ronly(m.ntotcampos)

list_tit(m.ncampo) = "SEL"
list_cam(m.ncampo) = "c_test.SEL"
list_ronly(m.ncampo) = .F.
list_pic(m.ncampo) = "LOGIC"
list_tam(m.ncampo) = 8*20
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "TIPO"
list_cam(m.ncampo) = "c_test.COLUNA14"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*40
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "AnoFat"
list_cam(m.ncampo) = "c_test.ACCOUNTANCYYEAR"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = "#####"
list_tam(m.ncampo) = 8*60
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "MONTH"
list_cam(m.ncampo) = "c_test.COLUNA1"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = "####"
list_tam(m.ncampo) = 8*40
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "COSTCENTER"
list_cam(m.ncampo) = "c_auxC.COSTCENTER"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*40
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "DOCUMENTDATE"
list_cam(m.ncampo) = "c_test.DOCUMENTDATE"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*40
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "DOCUMENTNUMBER"
list_cam(m.ncampo) = "c_test.DOCUMENTNUMBER"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*40
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "VENDORVATID"
list_cam(m.ncampo) = "c_test.COLUNA13"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*50
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "COSTUMERVATID"
list_cam(m.ncampo) = "c_test.COLUNA9"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*50
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "TOTAL"
list_cam(m.ncampo) = "c_test.COLUNA12"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = "####"
list_tam(m.ncampo) = 8*50
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "DOCUMENTSTATUS"
list_cam(m.ncampo) = "c_test.DOCUMENTSTATUS"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*50
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "UPDATEDON"
list_cam(m.ncampo) = "c_test.UPDATEDON"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*50
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "ID"
list_cam(m.ncampo) = "c_test.DOCUMENTID"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*50
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "CREATEDON"
list_cam(m.ncampo) = "c_test.CREATEDON"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*50
m.ncampo = m.ncampo + 1

list_tit(m.ncampo) = "DOCUMENTNAME"
list_cam(m.ncampo) = "c_test.DOCUMENTNAME"
list_ronly(m.ncampo) = .T.
list_pic(m.ncampo) = ""
list_tam(m.ncampo) = 8*50

m.Escolheu = .F.

browlist('Documentos BizDocs', 'c_test', 'c_test', .T., .F., .F., .T., .F., '', .T.)

If m.Escolheu = .F.
	Messagebox("Deve escolher um documento para associar!")
	Return .F.
Endif


If Used ("c_curBizDia")
	fecha("c_curBizDia")
Endif

Create Cursor c_curBizDia (DocumentId C(36),accountingMonth C(6),accountingNumber C(50),diaryCode C(20),diaryName C(20),SupplierVATID C(20),CustomerVATID C(20),InvoiceDate C(20),InvoiceNumber C(25),Total N(14,4),LaunchNumber C(10))

*mostrameisto("c_test")

Scan For c_test.SEL=.T.
	msg("aqui")
	TEXT to msel textmerge noshow
		-- Concrete example (illustrative values copied from anexoIns in the code):
INSERT INTO Anexos (
  Anexosstamp, Oritable, Tabnm, Resumo, Grupo, Recstamp, Uniqueid, Descricao, Bdados, Fullname,
  Fname, Fext, Flen, Tipo, Passw, Origem, Keylook, Tpdos, Tpdoc,
  Ausrinis, Ausrdata, Ausrhora, Eusrinis, Eusrdata, Eusrhora, Anexopaistamp, Assinatura, Timestamp, Anexoversaostamp,
  Versao, Idustamp, Usrhora, Marcada, Zipado, Bdadosstamp, Invisivel, Checkout, Cuserno, Cusername,
  Usnoopen, Usnaopen, Isemail, Emailid, Emaildata, Startwkf, Wtwstamp, Emailsubj, Privado, Lsgq,
  Fiscrel, Original, Filestorageid, Marcadoenviar
) VALUES (
  left(newid(),25), -- Anexosstamp (example GUID substring)
  'FO',
  'Compras a Fornecedores',
  'Criação de relação entre o PHC e o bizdocs para o documento '+ '<<fo.adoc>>',
  'Compras a Fornecedores', -- Grupo / U_Nomeproj (example)
  '<<fo.fostamp>>', -- Recstamp (example tpostamp)
  '', -- Uniqueid
  'Compra: Adicionado via bizdocs API',
  0x, -- Bdados (sample binary; real file bytes are used in code)
  '<<user_urlviewdocument>>'+'<<c_test.DOCUMENTID>>', -- Fullname left empty in code for Tipo=1
  '//arquivodigitalpp.bizdocs', -- Fname (file name without extension)
  'mobi/Documents/ViewDocument?do', -- Fext
  0, -- Flen (example file length)
  4, -- Tipo
  '', -- Passw
  'Compras a Fornecedores', -- Origem
  '', -- Keylook
  0, -- Tpdos
  0, -- Tpdoc
  'SA', -- Ausrinis
  '2026-02-11', -- Ausrdata
  '', -- Ausrhora
  'SA', -- Eusrinis
  '2026-02-11', -- Eusrdata
  '', -- Eusrhora
  '', -- Anexopaistamp
  0, -- Assinatura
  0, -- Timestamp
  '', -- Anexoversaostamp
  0, -- Versao
  '', -- Idustamp
  '14:30:00', -- Usrhora (example)
  0, -- Marcada
  0, -- Zipado
  '', -- Bdadosstamp
  0, -- Invisivel
  0, -- Checkout
  0, -- Cuserno
  '', -- Cusername
  0, -- Usnoopen
  '', -- Usnaopen
  0, -- Isemail
  '', -- Emailid
  '1900-01-01', -- Emaildata
  0, -- Startwkf
  '', -- Wtwstamp
  '', -- Emailsubj
  0, -- Privado
  0, -- Lsgq
  0, -- Fiscrel
  0, -- Original
  '', -- Filestorageid
  0 -- Marcadoenviar
);

	ENDTEXT
	msg("aqui2")
	If !u_sqlexec(msel)
		msg(msel)
		Return .F.
	Endif

	TEXT TO MSEL TEXTMERGE NOSHOW
		select * from do where dostamp='<<alltrim(fo.dostamp)>>'
	ENDTEXT

	If !u_sqlexec(msel,'c_do')
		msg("Erro a obter contabilidade:" + msel)
	Endif

	Try
		lcDocId = Iif(Vartype(c_test.DocumentId)="C", Alltrim(c_test.DocumentId), "")

		lcMonth = Iif(Vartype(c_test.coluna1)="N", Alltrim(Str(c_test.coluna1)), "")

		lcATCUD = Iif(Vartype(fo2.atcud)="C", Alltrim(fo2.atcud), "")

		lcDino = Iif(Vartype(c_do.dino)="C", Alltrim(c_do.dino), "")

		lcPlano = Iif(Vartype(fo.dilnoplano)="C", Alltrim(fo.dilnoplano), "")

		lcSupVAT = Iif(Vartype(c_test.coluna13)="C", Left(Alltrim(c_test.coluna13),20), "")

		lcCusVAT = Iif(Vartype(c_test.coluna9)="C", Left(Alltrim(c_test.coluna9),20), "")

		lcDate = Iif(Vartype(fo.pdata)="D", Dtoc(fo.pdata,1), "")

		lcInvNo = Iif(Vartype(fo.Adoc)="C", Alltrim(fo.Adoc), "")

		lnTotal = Iif(Vartype(fo.etotal)="N", fo.etotal, 0)

		lcLaunch = Iif(Vartype(fo.dilnoplano)="N", Alltrim(Str(fo.dilnoplano)), "")


		Insert Into c_curBizDia ;
			VALUES ( ;
			lcDocId, lcMonth, lcATCUD, lcDino, lcPlano, ;
			lcSupVAT, lcCusVAT, lcDate, lcInvNo, lnTotal, lcLaunch ;
			)




	Catch To oError
		Messagebox( ;
			"Error: " + Transform(oError.ErrorNo) + Chr(13) + ;
			"Message: " + oError.Message + Chr(13) + ;
			"Line: " + Transform(oError.Lineno), ;
			16, "INSERT Error")
	Endtry
*	mostrameisto("c_curBizDia")
Endscan


*******************Criar CURSOR em JSON ****************************
return
*lcJson = user_CursorToRequestsJson("c_curBizDia")
*msg(lcJson)


lcUrl = ;
	"https://nikepp.azurewebsites.net/api/Company/PT504419811/AccountingOperations"

lcBody = lcJson

loHttp = Createobject("MSXML2.ServerXMLHTTP")
* timeouts em ms: resolve, connect, send, receive
loHttp.setTimeouts(3000, 3000, 5000, 5000)

Try
	loHttp.Open("POST", lcUrl, .F.)
	loHttp.setRequestHeader("Content-Type", "application/json")
	loHttp.setRequestHeader("Authorization", "Bearer " + lcToken)
	loHttp.Send(lcBody)
Catch To loErr
	Messagebox( ;
		"Não foi possível ligar ao serviço externo." + Chr(13) + ;
		"O sistema continuará a funcionar normalmente." + Chr(13) + ;
		"Detalhe: " + loErr.Message, ;
		48, "Serviço indisponível" )
	isErros = .T.
Endtry
If isErros
	Return .F.
Endif

If loHttp.Status <> 200
	Messagebox(loHttp.responseText, 16)
	Return .F.
Endif