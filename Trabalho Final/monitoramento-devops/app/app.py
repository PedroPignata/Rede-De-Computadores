from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Monitoramento DevOps - Funcionando!</h1><p>Se você está vendo isso, seu ambiente Docker está perfeito.</p>"

if __name__ == '__main__':
    # Roda o servidor na porta 5000 e aceita conexões externas (0.0.0.0)
    app.run(host='0.0.0.0', port=5000, debug=True)