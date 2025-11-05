# 3.2 Testes com Cliente Python (teste_cliente.py)

import requests

TEST_ID_USUARIO = 4
TEST_ID_PRODUTO = 4 

# Teste API Usuários
print("=== TESTE USUÁRIOS (5001) ===")

# Teste 1: GET para listar todos os usuários
response = requests.get('http://localhost:5001/usuarios')
print("Lista de usuários:", response.json())

# Teste 2: POST para adicionar um novo usuário
novo_usuario = {"nome": "Maria Santos", "email": "maria@exemplo.com"}
response = requests.post('http://localhost:5001/usuarios', json=novo_usuario)
print("Novo usuário criado:", response.json())


# Teste API Produtos
print("\n=== TESTE PRODUTOS (5002) ===")

# Teste 3: GET para listar todos os produtos
response = requests.get('http://localhost:5002/produtos')
print("Lista de produtos:", response.json())

# Teste 4: POST para adicionar um novo produto
novo_produto = {"nome": "Tablet", "preco": 1800.00, "estoque": 8}
response = requests.post('http://localhost:5002/produtos', json=novo_produto)
print("Novo produto criado:", response.json())

# --- Testes de PUT (Atualizar) ---
print("\n=== TESTE PUT (Atualização) ===")

# Teste 5: PUT para atualizar o usuário (usa o ID 4 como exemplo)
dados_update = {"nome": "Maria Santos Nova", "email": "maria.nova@exemplo.com"}
url_user_put = f'http://localhost:5001/usuarios/{TEST_ID_USUARIO}'
response = requests.put(url_user_put, json=dados_update)
print(f"PUT Usuário {TEST_ID_USUARIO}: Status {response.status_code}, Nome: {response.json().get('nome')}")

# Teste 6: PUT para atualizar o produto (usa o ID 4 como exemplo)
dados_update_prod = {"preco": 2500.00, "estoque": 12}
url_prod_put = f'http://localhost:5002/produtos/{TEST_ID_PRODUTO}'
response = requests.put(url_prod_put, json=dados_update_prod)
print(f"PUT Produto {TEST_ID_PRODUTO}: Status {response.status_code}, Preço: {response.json().get('preco')}")


# --- Testes de DELETE (Remoção) ---
print("\n=== TESTE DELETE (Remoção) ===")

# Teste 7: DELETE para remover o produto (usa o ID 4 como exemplo)
url_prod_delete = f'http://localhost:5002/produtos/{TEST_ID_PRODUTO}'
response = requests.delete(url_prod_delete)
print(f"DELETE Produto {TEST_ID_PRODUTO}: Status {response.status_code} (204 = Sucesso)")

# Teste 8: GET para confirmar a remoção (deve dar 404)
response = requests.get(url_prod_delete)
print(f"GET após DELETE: Status {response.status_code} (404 = Removido)")


# --- Testes da Terceira API (Pedidos - 5003) ---
print("\n=== TESTE API PEDIDOS (5003) - Interação ===")

# Teste 9: POST para criar um Pedido (usa Usuario 1 e Produto 1, que existem)
pedido_data = {
    "id_usuario": 1, 
    "itens": [{"id_produto": 1, "quantidade": 1}],
    "data_pedido": "2025-11-05"
}
url_pedido_post = 'http://localhost:5003/pedidos'
response = requests.post(url_pedido_post, json=pedido_data)

if response.status_code == 201:
    print(f"POST Pedido: Status 201, ID Pedido: {response.json().get('id')}, Status: {response.json().get('status')}")
else:
    
    print(f"POST Pedido FALHOU: Status {response.status_code}, Erro: {response.json().get('erro')}")

# Teste 10: GET para listar Pedidos
response = requests.get(url_pedido_post)
print(f"GET Pedidos: Status {response.status_code}, Total: {len(response.json())} pedidos")