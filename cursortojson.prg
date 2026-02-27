LPARAMETERS tcAlias

LOCAL lcJson, llFirst, lcTotal, lcTimestamp, ltNow, lnSec, lnMs

IF !USED(tcAlias)
    RETURN '{ "requests": [] }'
ENDIF

SELECT (tcAlias)
GO TOP

lcJson = '{ "requests": ['
llFirst = .T.

SCAN
    IF !llFirst
        lcJson = lcJson + ","
    ENDIF
    llFirst = .F.

    lcTotal = STRTRAN(ALLTRM(TRANSFORM(c_curbizdia.Total)), ",", ".")
    ltNow = DATETIME()
    lnSec = SECONDS()
    lnMs = INT((lnSec - INT(lnSec)) * 1000)
    lcTimestamp = ;
        RIGHT("0000" + LTRIM(STR(YEAR(ltNow))), 4) + "-" + ;
        RIGHT("00" + LTRIM(STR(MONTH(ltNow))), 2) + "-" + ;
        RIGHT("00" + LTRIM(STR(DAY(ltNow))), 2) + "T" + ;
        RIGHT("00" + LTRIM(STR(HOUR(ltNow))), 2) + ":" + ;
        RIGHT("00" + LTRIM(STR(MINUTE(ltNow))), 2) + ":" + ;
        RIGHT("00" + LTRIM(STR(SEC(ltNow))), 2) + "." + ;
        RIGHT("000" + LTRIM(STR(lnMs)), 3) + "Z"

    lcJson = lcJson + ;
    '{' + ;
    '"documentId":"' + alltrim(c_curbizdia.DocumentId) + '",' + ;
    '"accountancyYear":'+fo.foano+',' + ;
    '"accountancyMonth":'+MONTH(fo.docdata)+',' + ;
    '"accountingNumber":"' + alltrim(c_curbizdia.accountingNumber) + '",' + ;
    '"documentType":"FT",' + ;
    '"diaryCode":"' + alltrim(c_curbizdia.diaryCode) + '",' + ;
    '"diaryName":"' + alltrim(c_curbizdia.diaryName) + '",' + ;
    '"accountingComment":"Compra",' + ;
    '"accountingUserName":"'+fo.usrinis+'",' + ;
    '"accountingType":"Manual",' + ;
    '"fields":{' + ;
    '"invoiceNumber":"' + alltrim(c_curbizdia.InvoiceNumber) + '",' + ;
    '"invoiceDate":"' + fo.docdata + '",' + ;
    '"vatid":"' + alltrim(c_curbizdia.SupplierVATID) + '",' + ;
    '"total":' + lcTotal + ',' + ;
    '"customerVATID":"' + alltrim(c_curbizdia.CustomerVATID) + '",' + ;
    '"documentType":"FT",' + ;
    '"supplierDescription":"'+alltrim(fo.nome)+'",' + ;
    '"customerDescription":"Barrinho",' + ;
    '"taxLines":[{"netAmount":'+lcTotal+',"taxRate":23.00,"taxAmount":'+fo.eivain+',"taxRateType":"NOR","taxCountryRegion":"PT"}],' + ;
    '"documentTypeCode":"1",' + ;
    '"documentTypeDescription":"FT",' + ;
    '"launchNumber":"' + alltrim(c_curbizdia.LaunchNumber) + '",' + ;
    '"netAmountSum":'+lcTotal+',' + ;
    '"taxAmountSum":'+fo.eivain+',' + ;
    '"discount":0,' + ;
    '"country":"PT",' + ;
    '"operationRegion":"Portugal Continental",' + ;
    '"activitySector":"Consulting",' + ;
    '"fiscalEntity":"Nacional-Normal",' + ;
    '"entityType":"F",' + ;
    '"entityName":"Fornecedores",' + ;
    '"retention":0,' + ;
    '"currency":"EUR",' + ;
    '"additionalFields":[{"account":"123","debit":0,"credit":0,"tax":"0.00","deductionPercentage":0,"recapitulation":true,"entityType":"F","supplierVatId":"' + alltrim(c_curbizdia.SupplierVATID) + '","description":"' + alltrim(c_curbizdia.InvoiceNumber) + '"}]' + ;
    '},' + ;
    '"timestamp":"' + lcTimestamp + '"' + ;
    '}'
ENDSCAN

lcJson = lcJson + '] }'

RETURN lcJson