# API de Dados Protegidos (valida token)

from flask import Flask, jsonify, request
import jwt
from functools import wraps # Essencial para criar decoradores que funcionam

# Continua com a mesma chave "secreta" da API anterior (mantenha a consistência!)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'

# Dados fictícios (Onde o João e a Maria guardam suas notas)
dados_usuarios = {
    'joao': ['nota1: 8.5', 'nota2: 7.0'],
    'maria': ['nota1: 9.0', 'nota2: 8.5']
}

# O famoso Decorador: Ele verifica o token antes de permitir o acesso à função
def token_obrigatorio(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        # Tenta pegar o token no header 'Authorization'.
        # Espera-se que venha como 'Bearer <token>'.
        token = request.headers.get('Authorization')

        if not token:
            # Se nem um token foi enviado, a festa acaba na porta.
            return jsonify({'erro': 'Token necessário'}), 401
        
        try:
            # Remove o 'Bearer ' do início (o que se espera no padrão JWT)
            if token.startswith('Bearer '):
                token = token[7:]

            # Decodifica o token usando a chave secreta.
            # Se a chave não bater ou o token tiver expirado, o decode falha.
            dados = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            usuario_atual = dados['user'] # Pega o 'user' que foi colocado no token

        except:
            # Token inválido (expirado, modificado, chave errada, etc.)
            return jsonify({'erro': 'Token inválido'}), 401
        
        # Se tudo deu certo, chama a função original (dados_protegidos)
        # e passa o usuário extraído do token para ela.
        return f(usuario_atual, *args, **kwargs)

    return decorador

# Rota que precisa do token para funcionar!
@app.route('/dados')
@token_obrigatorio # A magia acontece aqui!
def dados_protegidos(usuario_atual):
    if usuario_atual in dados_usuarios:
        return jsonify({
            'usuario': usuario_atual,
            'dados': dados_usuarios[usuario_atual]
        })
    
    # Este erro só ocorreria se o token fosse válido, mas o usuário
    # do token fosse apagado do dicionário de dados (situação rara).
    return jsonify({'erro': 'Usuário não encontrado'}), 404

if __name__ == '__main__':
    # Roda em uma porta diferente (5001) para evitar conflito com a API de login
    app.run(port=5001)