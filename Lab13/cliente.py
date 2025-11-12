# cliente.py

import requests
import time 

class ClienteJWT:
    def __init__(self):
        self.url_auth = "http://localhost:5000"
        self.url_dados = "http://localhost:5001"
        self.token = None

    def login(self, usuario, senha):
        print(f"\n[AÇÃO] Tentando login com Usuário: {usuario}")
        try:
            resposta = requests.get(f"{self.url_auth}/login/{usuario}/{senha}")

            if resposta.status_code == 200:
                self.token = resposta.json()['token']
                print("✅ SUCESSO! Login realizado. Token recebido.")
                return True
            else:
                print(f"❌ FALHA! Login: {resposta.json()['erro']}")
                self.token = None 
                return False

        except requests.exceptions.ConnectionError:
            print("❌ ERRO DE CONEXÃO! Verifique se a API de Autenticação (5000) está rodando.")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return False

    def buscar_dados(self):
        print("\n[AÇÃO] Tentando acessar dados protegidos...")
        
        if not self.token:
            pass 

        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}

        try:
            resposta = requests.get(f"{self.url_dados}/dados", headers=headers)

            if resposta.status_code == 200:
                dados = resposta.json()
                print(f"✅ SUCESSO! Dados de {dados['usuario']} recebidos:")
                for item in dados['dados']:
                    print(f" - {item}")
            else:
                print(f"❌ FALHA! Resposta da API de Dados (Status {resposta.status_code}): {resposta.json()['erro']}")

        except requests.exceptions.ConnectionError:
            print("❌ ERRO DE CONEXÃO! Verifique se a API de Dados (5001) está rodando.")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

# --- ROTEIRO DE TESTES ---

if __name__ == '__main__':
    
    # Usuário a ser usado nos testes (existe na auth_api)
    USUARIO_VALIDO = 'joao'
    SENHA_VALIDA = 'senha123'

    # --- Teste 1: Login Bem-sucedido (e Teste de credenciais inválidas)
    print("\n" + "="*50)
    print("           ROTEIRO DE TESTES INICIADO")
    print("="*50)

    # 1.1 Login Bem-sucedido
    print("\n--- Teste 1: Login Bem-sucedido ---")
    cliente = ClienteJWT()
    cliente.login(USUARIO_VALIDO, SENHA_VALIDA)
    
    # --- Teste 2: Acesso a Dados Protegidos (com token válido)
    print("\n--- Teste 2: Acesso a Dados Protegidos ---")
    cliente.buscar_dados()
    
    # --- Teste 4: Token Inválido (Parte 1: Sem token) ---
    print("\n--- Teste 4.1: Acesso Sem Token ---")
    cliente_sem_token = ClienteJWT()
    cliente_sem_token.buscar_dados()
    
    # --- Teste 4: Token Inválido (Parte 2: Token Malformado) ---
    print("\n--- Teste 4.2: Acesso com Token Malformado ---")
    cliente_malformado = ClienteJWT()
    cliente_malformado.token = 'definitivamente.nao.e.um.token.valido' 
    cliente_malformado.buscar_dados()
    
    # --- Teste 3: Token Expirado ---
    # REQUER: Alterar 'minutes=30' para 'seconds=10' na auth_api.py E reiniciar essa API!
    print("\n--- Teste 3: Token Expirado (Requer API de Auth com expiração de 10s) ---")
    print("ATENÇÃO: Requer que você reinicie a API de Autenticação com o tempo de 10s!")
    cliente_expira = ClienteJWT()
    if cliente_expira.login(USUARIO_VALIDO, SENHA_VALIDA):
        print("Aguardando 12 segundos para o token expirar...")
        time.sleep(12)
        cliente_expira.buscar_dados()
    
    print("\n" + "="*50)
    print("           ROTEIRO DE TESTES CONCLUÍDO")
    print("="*50)