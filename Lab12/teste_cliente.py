# 3.2 Testes com Cliente Python (teste_cliente.py)

import requests

# Teste API Usuários
print("=== TESTE USUÁRIOS ===")

# Teste 1: GET para listar todos os usuários
response = requests.get('http://localhost:5001/usuarios')
print("Lista de usuários:", response.json())

# Teste 2: POST para adicionar um novo usuário
novo_usuario = {"nome": "Maria Santos", "email": "maria@exemplo.com"}
response = requests.post('http://localhost:5001/usuarios', json=novo_usuario)
print("Novo usuário criado:", response.json())


# Teste API Produtos
print("\n=== TESTE PRODUTOS ===")

# Teste 3: GET para listar todos os produtos
response = requests.get('http://localhost:5002/produtos')
print("Lista de produtos:", response.json())

# Teste 4: POST para adicionar um novo produto
novo_produto = {"nome": "Tablet", "preco": 1800.00, "estoque": 8}
response = requests.post('http://localhost:5002/produtos', json=novo_produto)
print("Novo produto criado:", response.json())