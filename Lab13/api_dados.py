# API de Dados Protegidos (valida token)

from flask import Flask, jsonify, request
import jwt
from functools import wraps 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'

dados_usuarios = {
    'joao': ['nota1: 8.5', 'nota2: 7.0'],
    'maria': ['nota1: 9.0', 'nota2: 8.5']
}

def token_obrigatorio(f):
    @wraps(f)
    def decorador(*args, **kwargs):

        token = request.headers.get('Authorization')

        if not token:
           
            return jsonify({'erro': 'Token necessário'}), 401
        
        try:

            if token.startswith('Bearer '):
                token = token[7:]

            dados = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            usuario_atual = dados['user'] 

        except:
            
            return jsonify({'erro': 'Token inválido'}), 401

        return f(usuario_atual, *args, **kwargs)

    return decorador

@app.route('/dados')
@token_obrigatorio 
def dados_protegidos(usuario_atual):
    if usuario_atual in dados_usuarios:
        return jsonify({
            'usuario': usuario_atual,
            'dados': dados_usuarios[usuario_atual]
        })
    
    return jsonify({'erro': 'Usuário não encontrado'}), 404

if __name__ == '__main__':
    
    app.run(port=5001)