# API de Produtos (api_produtos.py)

from flask import Flask, jsonify, request

app = Flask(__name__)

# Lista simulada de produtos
produtos = [
    {"id": 1, "nome": "Notebook", "preco": 3500.00, "estoque": 10},
    {"id": 2, "nome": "Smartphone", "preco": 2500.00, "estoque": 15}
]
# Seus comandos POST anteriores devem ter adicionado o Monitor no ID 4.

# Rota GET para listar todos os produtos
@app.route('/produtos', methods=['GET'])
def get_produtos():
    return jsonify(produtos)

# Rota POST para adicionar um novo produto
@app.route('/produtos', methods=['POST'])
def add_produto():
    novo_produto = request.json
    novo_produto['id'] = len(produtos) + 1
    produtos.append(novo_produto)
    return jsonify(novo_produto), 201

# --- Rota Corrigida e Expandida (GET, PUT, DELETE) ---
@app.route('/produtos/<int:produto_id>', methods=['GET', 'PUT', 'DELETE'])
def gerenciar_produto(produto_id):
    # Encontra o índice (posição) do produto na lista
    index = next((i for i, p in enumerate(produtos) if p['id'] == produto_id), None)

    if index is None:
        return jsonify({"erro": "Produto não encontrado"}), 404

    # Lógica GET (Buscar)
    if request.method == 'GET':
        return jsonify(produtos[index])

    # Lógica PUT (Atualizar)
    elif request.method == 'PUT':
        dados_atualizados = request.json
        
        # Atualiza apenas os campos que vieram no body
        produtos[index].update(dados_atualizados)
        produtos[index]['id'] = produto_id
        
        return jsonify(produtos[index])

    # Lógica DELETE (Remover)
    elif request.method == 'DELETE':
        del produtos[index]
        return '', 204 # Resposta 204 No Content

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(port=5002, debug=True)