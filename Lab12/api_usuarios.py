# API de Usuários (api_usuarios.py)

from flask import Flask, jsonify, request

app = Flask(__name__)

# Lista simulada de usuários
usuarios = [
    {"id": 1, "nome": "Ana Silva", "email": "ana@exemplo.com"},
    {"id": 2, "nome": "Carlos Oliveira", "email": "carlos@exemplo.com"}
]

# Rota GET para listar todos os usuários
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    return jsonify(usuarios)

# Rota POST para adicionar um novo usuário
@app.route('/usuarios', methods=['POST'])
def add_usuario():
    # Obtém os dados JSON da requisição
    novo_usuario = request.json
    
    # Atribui um novo ID (simplesmente len(usuarios) + 1)
    novo_usuario['id'] = len(usuarios) + 1
    
    # Adiciona o novo usuário à lista
    usuarios.append(novo_usuario)
    
    # Retorna o usuário criado com o código de status 201 (Created)
    return jsonify(novo_usuario), 201

# Rota GET para obter um usuário por ID
@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    # Procura o usuário na lista pelo ID
    # next() retorna o primeiro item que satisfaz a condição
    # ou 'None' se não encontrar
    usuario = next((u for u in usuarios if u['id'] == usuario_id), None)
    
    if usuario:
        # Retorna o usuário encontrado
        return jsonify(usuario)
    else:
        # Retorna erro 404 (Not Found) se o usuário não for encontrado
        return jsonify({"erro": "Usuário não encontrado"}), 404

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(port=5001, debug=True)