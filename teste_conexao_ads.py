import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def validar_conexao_ads():
    print("--- Iniciando Teste de Autenticação ---")
    try:
        # Carrega as configurações do seu arquivo yaml
        client = GoogleAdsClient.load_from_storage("google-ads.yaml")
        
        # Chama o serviço para listar as contas acessíveis
        customer_service = client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()

        print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        print("Contas encontradas:")
        
        for resource_name in accessible_customers.resource_names:
            print(f"- {resource_name}")
            
    except GoogleAdsException as ex:
        print(f"❌ ERRO NA API DO GOOGLE ADS:")
        for error in ex.failure.errors:
            print(f"\tError with message: {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        print("\nVerifique se o seu 'Refresh Token' ainda é válido ou se o 'Developer Token' está correto.")
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

if __name__ == "__main__":
    validar_conexao_ads()