
# auth_manager.py

import requests
from requests.auth import HTTPBasicAuth
import time
import json
import os

# --- 1. VARIÁVEL DE MÓDULO PARA ARMAZENAR O TOKEN ---
# O token e o tempo de expiração serão armazenados aqui, acessíveis após a inicialização.
TOKEN_INFO = {
    "access_token": None,
    "expiry_timestamp": 0  # Unix timestamp de quando o token expira
}

# --- 2. CONFIGURAÇÕES (Substitua pelos seus valores) ---
# O Access Token URL é {{api-bzd-identity}}
TOKEN_URL = "https://arquivodigitalpp.bizdocs.mobi/identity/connect/token" 
# O Client ID é {{api-bzd-identity-client_id}}
CLIENT_ID = "Trigenius" 
# O Client Secret é {{api-bzd-identity-client_secret}}
CLIENT_SECRET = "DACXVOD743ZGGpikJnk88FdFCYo5d0n9"
# O Username é {{api-bzd-user_email}}
USERNAME = "tiago.amaro@trigenius.pt" 
# O Password é {{api-bzd-user_password}}
PASSWORD = "Tamaro@2023" 
# O Scope é 'api1 api2'
SCOPE = "api1 api2" 

# --- 3. FUNÇÃO PRINCIPAL PARA OBTER/ATUALIZAR O TOKEN ---
def get_access_token():
    """
    Retorna um token de acesso válido. Se o token atual estiver expirado, solicita um novo.
    """
    # 5 minutos = 300 segundos. Usamos uma margem de segurança de 60 segundos
    SAFETY_MARGIN = 60 

    # Verifica se o token atual ainda é válido
    if TOKEN_INFO["access_token"] and (TOKEN_INFO["expiry_timestamp"] > time.time() + SAFETY_MARGIN):
        print("✅ Token existente ainda válido.")
        return TOKEN_INFO["access_token"]

    # Se o token estiver ausente ou prestes a expirar, solicita um novo
    print("⏳ A solicitar novo Access Token...")
    
    payload = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "scope": SCOPE
    }
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

    try:
        response = requests.post(TOKEN_URL, data=payload, auth=auth)
        response.raise_for_status() 
        token_data = response.json()
        
        token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 300) # Assumimos 300s (5min) se não vier na resposta
        
        # Atualiza a variável de módulo (global dentro do ficheiro)
        TOKEN_INFO["access_token"] = token
        TOKEN_INFO["expiry_timestamp"] = time.time() + expires_in
        
        print(f"✅ Novo Access Token obtido. Válido por {expires_in} segundos.")
        return token

    except requests.exceptions.HTTPError as errh:
        print(f"❌ Erro HTTP ao obter token: {errh}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"❌ Erro na Conexão: {err}")
        return None

# --- Exemplo de Teste/Inicialização ---
if __name__ == "__main__":
    token = get_access_token()
    if token:
        print(f"\nToken de Acesso: {token[:20]}...")
        print(f"Expira em: {time.ctime(TOKEN_INFO['expiry_timestamp'])}")
        
        # Simular uso após 4.5 minutos para forçar a atualização na próxima chamada
        print("\n--- Simulando 4.5 minutos de uso... ---")
        time.sleep(270) 
        
        token = get_access_token() # Deve solicitar um novo token
        if token:
            print(f"\nToken de Acesso ATUALIZADO: {token[:20]}...")