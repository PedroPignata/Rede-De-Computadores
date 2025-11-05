# API de Usuários (api_usuarios.py)

from flask import Flask, jsonify, request

app = Flask(__name__)

# Lista simulada de usuários
usuarios = [
    {"id": 1, "nome": "Ana Silva", "email": "ana@exemplo.com"},
    {"id": 2, "nome": "Carlos Oliveira", "email": "carlos@exemplo.com"}
]
# Seus comandos POST anteriores devem ter adicionado o Pedro no ID 4.

# Rota GET para listar todos os usuários
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    return jsonify(usuarios)

# Rota POST para adicionar um novo usuário
@app.route('/usuarios', methods=['POST'])
def add_usuario():
    novo_usuario = request.json
    novo_usuario['id'] = len(usuarios) + 1
    usuarios.append(novo_usuario)
    return jsonify(novo_usuario), 201

# --- Rota Corrigida e Expandida (GET, PUT, DELETE) ---
@app.route('/usuarios/<int:usuario_id>', methods=['GET', 'PUT', 'DELETE'])
def gerenciar_usuario(usuario_id):
    # Encontra o índice (posição) do usuário na lista
    index = next((i for i, u in enumerate(usuarios) if u['id'] == usuario_id), None)

    if index is None:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    # Lógica GET (Buscar)
    if request.method == 'GET':
        return jsonify(usuarios[index])

    # Lógica PUT (Atualizar)
    elif request.method == 'PUT':
        dados_atualizados = request.json
        
        # Atualiza apenas os campos que vieram no body
        usuarios[index].update(dados_atualizados)
        usuarios[index]['id'] = usuario_id
        
        return jsonify(usuarios[index])

    # Lógica DELETE (Remover)
    elif request.method == 'DELETE':
        del usuarios[index]
        return '', 204 # Resposta 204 No Content

# Inicia o servidor Flask
if __name__ == '__main__':
    app.run(port=5001, debug=True)