import requests
import urllib3

# Desativa avisos de conexões não seguras
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("--- Iniciando Teste de Emergência ---")

try:
    # verify=False pula a verificação de certificado que está falhando
    response = requests.get('https://www.google.com', timeout=10, verify=False)
    print(f"✅ Conexão estabelecida (Modo Inseguro). Status: {response.status_code}")
    print("Isso confirma que o problema é no Handshake de Certificados da sua rede.")
except Exception as e:
    print(f"❌ Mesmo sem verificação, o erro persiste: {e}")