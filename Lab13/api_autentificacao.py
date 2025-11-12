# API de Autenticação (gera token)

from flask import Flask, jsonify
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-secreta'

usuarios = {
    'joao': 'senha123',
    'maria': 'abc123'
}

@app.route('/login/<username>/<password>')
def login(username, password):
    if username in usuarios and usuarios[username] == password:

        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'erro': 'Credenciais inválidas'}), 401

if __name__ == '__main__':
    app.run(port=5000)