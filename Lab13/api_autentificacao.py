# API de Autenticação (gera token)

from flask import Flask, jsonify
import jwt
import datetime

# Aviso: "minha-chave-secreta" não é secreta de verdade.
# Troque isso em produção! Sério, por favor.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'

# Usuários para teste (e para mostrar que autenticação é só um grande dicionário)
usuarios = {
    'joao': 'senha123',
    'maria': 'abc123'
}

@app.route('/login/<username>/<password>')
def login(username, password):
    if username in usuarios and usuarios[username] == password:
        # Criar token JWT
        # O token dura 30 minutos. Depois disso, ele se aposenta.
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})

    # Erro 401: A porta está fechada e suas credenciais não servem.
    return jsonify({'erro': 'Credenciais inválidas'}), 401

if __name__ == '__main__':
    app.run(port=5000)