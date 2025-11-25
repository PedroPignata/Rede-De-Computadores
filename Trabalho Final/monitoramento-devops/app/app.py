from flask import Flask, jsonify, render_template
import requests
import time
import socket
import psycopg2
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)

# Variável para controlar spam de alertas (simples)
# Armazena o último status para saber se mudou
ultimo_status = {
    "web": True,
    "db": True,
    "smtp": True
}

# --- FUNÇÃO DE ENVIAR E-MAIL (Requisito: Notificação) ---
def enviar_alerta_email(servico, erro):
    msg_content = f"""
    ALERTA CRÍTICO DE SISTEMA
    --------------------------
    O serviço: {servico}
    Está: INDISPONÍVEL (OFFLINE)
    Data: {datetime.now()}
    Erro técnico: {erro}
    
    Ação recomendada: Verificar logs do container imediatamente.
    """
    
    msg = MIMEText(msg_content)
    msg['Subject'] = f'CRÍTICO: {servico} caiu!'
    msg['From'] = 'monitor@devops.local'
    msg['To'] = 'admin@devops.local'

    try:
        # Conecta no nosso container MailHog (smtp-alvo) na porta 1025
        s = smtplib.SMTP('smtp-alvo', 1025)
        s.send_message(msg)
        s.quit()
        print(f"📧 E-mail de alerta enviado para {servico}!")
    except Exception as e:
        print(f"❌ Falha ao enviar e-mail: {e}")

# --- FUNÇÕES DE MONITORAMENTO ---

def checar_web_server():
    url = "http://web-alvo"
    resultado = {"servico": "Web Server (Nginx)", "status_online": False, "latencia_ms": 0, "detalhes": ""}
    
    try:
        inicio = time.time()
        requests.get(url, timeout=5)
        fim = time.time()
        resultado["status_online"] = True
        resultado["latencia_ms"] = round((fim - inicio) * 1000, 2)
        resultado["detalhes"] = "HTTP 200 OK"
    except Exception as e:
        resultado["detalhes"] = str(e)
        
    # Lógica de Disparo de E-mail
    verificar_mudanca_status("web", resultado["servico"], resultado["status_online"], resultado["detalhes"])
    return resultado

def checar_banco_dados():
    resultado = {"servico": "Banco de Dados (Postgres)", "status_online": False, "latencia_ms": 0, "detalhes": ""}
    try:
        inicio = time.time()
        conn = psycopg2.connect(host="db-alvo", user="postgres", password="senha_secreta", connect_timeout=3)
        conn.close()
        fim = time.time()
        resultado["status_online"] = True
        resultado["latencia_ms"] = round((fim - inicio) * 1000, 2)
        resultado["detalhes"] = "Conexão aceita"
    except Exception as e:
        resultado["detalhes"] = str(e)

    verificar_mudanca_status("db", resultado["servico"], resultado["status_online"], resultado["detalhes"])
    return resultado

def checar_smtp():
    resultado = {"servico": "Servidor SMTP (MailHog)", "status_online": False, "latencia_ms": 0, "detalhes": ""}
    try:
        inicio = time.time()
        s = smtplib.SMTP('smtp-alvo', 1025, timeout=3)
        s.quit()
        fim = time.time()
        resultado["status_online"] = True
        resultado["latencia_ms"] = round((fim - inicio) * 1000, 2)
        resultado["detalhes"] = "Serviço SMTP respondendo"
    except Exception as e:
        resultado["detalhes"] = str(e)
        
    verificar_mudanca_status("smtp", resultado["servico"], resultado["status_online"], resultado["detalhes"])
    return resultado

def verificar_mudanca_status(chave, nome_servico, esta_online, erro):
    global ultimo_status
    # Se estava online (True) e agora caiu (False), manda email
    if ultimo_status[chave] and not esta_online:
        enviar_alerta_email(nome_servico, erro)
    
    # Atualiza o status atual
    ultimo_status[chave] = esta_online

# --- ROTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/monitorar')
def monitorar():
    r1 = checar_web_server()
    r2 = checar_banco_dados()
    r3 = checar_smtp()
    return jsonify([r1, r2, r3])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)