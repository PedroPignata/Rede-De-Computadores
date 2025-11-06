# Cliente (usa as APIs)

import requests

# Lembrete: Você precisará ter a biblioteca 'requests' instalada
# (pip install requests)

class ClienteJWT:
    # 🌍 Configuração de Endpoints
    def __init__(self):
        self.url_auth = "http://localhost:5000"  # API que gera o token
        self.url_dados = "http://localhost:5001" # API que exige o token
        self.token = None # Onde guardaremos nosso "passe"

    # 🔑 Tenta fazer login e obter o token
    def login(self, usuario, senha):
        try:
            # Chama a API de Login (porta 5000)
            resposta = requests.get(f"{self.url_auth}/login/{usuario}/{senha}")

            if resposta.status_code == 200:
                self.token = resposta.json()['token']
                # \u2705 é o emoji de check mark
                print(f"\u2705 Login realizado! Token recebido.")
                return True
            else:
                # \u274C é o emoji de 'X'
                print(f"\u274C Login falhou! ({resposta.json()['erro']})")
                return False
        except requests.exceptions.ConnectionError:
            print(f"\u274C Erro de conexão. Certifique-se de que a API de Login (Porta 5000) está rodando.")
            return False
        except Exception as e:
            print(f"\u274C Ocorreu um erro inesperado: {e}")
            return False

    # 🛡️ Tenta acessar a rota protegida com o token
    def buscar_dados(self):
        if not self.token:
            # \u26A0\uFE0F é o emoji de alerta
            print("\u26A0\uFE0F Faça login primeiro. Token ausente.")
            return

        # Monta o cabeçalho (Header) padrão para JWT: 'Authorization: Bearer <token>'
        headers = {'Authorization': f'Bearer {self.token}'}

        try:
            # Chama a API Protegida (porta 5001) enviando o token no header
            resposta = requests.get(f"{self.url_dados}/dados", headers=headers)

            if resposta.status_code == 200:
                dados = resposta.json()
                print(f"\n\u25AD Dados de {dados['usuario']}:")
                for item in dados['dados']:
                    print(f" - {item}")
            else:
                # Se não for 200, algo deu errado (ex: token inválido 401, usuário não encontrado 404)
                print(f"\u274C Erro: {resposta.json()}")
        except requests.exceptions.ConnectionError:
            print(f"\u274C Erro de conexão. Certifique-se de que a API de Dados (Porta 5001) está rodando.")
        except Exception as e:
            print(f"\u274C Ocorreu um erro inesperado: {e}")

# --- Exemplo de Uso (Para rodar no final do arquivo) ---

if __name__ == '__main__':
    cliente = ClienteJWT()
    
    print("--- 1. Tentativa de Login e Acesso com SUCESSO (Usuário: joao) ---")
    if cliente.login('joao', 'senha123'):
        cliente.buscar_dados()
    
    print("\n--- 2. Tentativa de Acesso SEM Token (Deverá falhar) ---")
    cliente_sem_login = ClienteJWT()
    cliente_sem_login.buscar_dados()
    
    print("\n--- 3. Tentativa de Login com FALHA (Senha errada) ---")
    cliente.login('joao', 'senha_errada')