from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Lista simulada de pedidos
pedidos = []
next_pedido_id = 1

@app.route('/pedidos', methods=['GET'])
def get_pedidos():
    """Lista todos os pedidos."""
    return jsonify(pedidos)

@app.route('/pedidos', methods=['POST'])
def add_pedido():
    """Cria um novo pedido com validação nas outras APIs."""
    global next_pedido_id
    novo_pedido = request.json
    
    # --- 1. Realizar Interações com Outras APIs (Validação) ---
    
    # 1.1. Validar Usuário (API 5001)
    user_id = novo_pedido.get('id_usuario')
    if not user_id:
        return jsonify({"erro": "ID do usuário é obrigatório"}), 400
        
    try:
        # Tenta buscar o usuário na API 5001
        response_user = requests.get(f'http://localhost:5001/usuarios/{user_id}')
        if response_user.status_code != 200:
            return jsonify({"erro": f"Usuário {user_id} não encontrado na API 5001"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"erro": "API de Usuários (5001) inacessível"}), 503

    # 1.2. Validar Produtos (API 5002) - Simplificado
    if not novo_pedido.get('itens'):
        return jsonify({"erro": "O pedido deve ter itens"}), 400
        
    for item in novo_pedido['itens']:
        product_id = item.get('id_produto')
        
        # Tenta buscar o produto na API 5002
        try:
            response_product = requests.get(f'http://localhost:5002/produtos/{product_id}')
            if response_product.status_code != 200:
                return jsonify({"erro": f"Produto {product_id} não encontrado na API 5002"}), 404
        except requests.exceptions.ConnectionError:
            return jsonify({"erro": "API de Produtos (5002) inacessível"}), 503
        
        # Aqui, no mundo real, faríamos a checagem de estoque e o PUT para diminuir!
        
    # --- 2. Criação do Pedido ---
    
    # Se todas as validações passarem:
    novo_pedido['id'] = next_pedido_id
    novo_pedido['status'] = 'Aprovado'
    pedidos.append(novo_pedido)
    next_pedido_id += 1
    
    return jsonify(novo_pedido), 201

# Inicia o servidor Flask
if __name__ == '__main__':
    # Esta API de Pedidos rodará na porta 5003
    app.run(port=5003, debug=True)