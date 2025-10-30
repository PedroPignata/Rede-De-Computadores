# API de Produtos (api_produtos.py)

from flask import Flask, jsonify, request

app = Flask(__name__)

# Lista simulada de produtos
produtos = [
    {"id": 1, "nome": "Notebook", "preco": 3500.00, "estoque": 10},
    {"id": 2, "nome": "Smartphone", "preco": 2500.00, "estoque": 15}
]

# Rota GET para listar todos os produtos
@app.route('/produtos', methods=['GET'])
def get_produtos():
    return jsonify(produtos)

# Rota POST para adicionar um novo produto
@app.route('/produtos', methods=['POST'])
def add_produto():
    # Obtém os dados JSON da requisição
    novo_produto = request.json
    
    # Atribui um novo ID
    novo_produto['id'] = len(produtos) + 1
    
    # Adiciona o novo produto à lista
    produtos.append(novo_produto)
    
    # Retorna o produto criado com o código de status 201 (Created)
    return jsonify(novo_produto), 201

# Rota GET para obter um produto por ID
@app.route('/produtos/<int:produto_id>', methods=['GET'])
def get_produto(produto_id):
    # Procura o produto na lista pelo ID
    # next() retorna o primeiro item que satisfaz a condição
    # ou 'None' se não encontrar
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    
    if produto:
        # Retorna o produto encontrado
        return jsonify(produto)
    else:
        # Retorna erro 404 (Not Found) se o produto não for encontrado
        return jsonify({"erro": "Produto não encontrado"}), 404

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(port=5002, debug=True)