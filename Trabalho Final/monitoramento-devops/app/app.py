from flask import Flask, jsonify, render_template
import requests
import time
import socket
import psycopg2
import smtplib
import hashlib
import os
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)

# --- CONFIGURAÇÕES GLOBAIS ---
ARQUIVO_VIGIADO = "protegido.conf"
HASH_ORIGINAL = "" 
ULTIMO_STATUS = {
    "web": True, 
    "db": True, 
    "smtp": True, 
    "seguranca": True
}

# --- FUNÇÃO DE ENVIAR E-MAIL (VIA MAILHOG) ---
def enviar_alerta_email(titulo, mensagem):
    print(f"📧 Enviando alerta para MailHog: {titulo}...")
    
    # Configuração da Mensagem
    msg = MIMEText(f"""
    ALERTA CRÍTICO - MONITORAMENTO DEVOPS
    -------------------------------------
    Evento: {titulo}
    Data/Hora: {datetime.now()}
    
    Detalhes Técnicos:
    {mensagem}
    
    Ação Necessária: Verificar logs do container imediatamente.
    """)
    
    # Cabeçalhos do E-mail
    msg['Subject'] = f'🚨 ALERTA: {titulo}'
    msg['From'] = 'sistema@monitoramento.local'  # Remetente Fictício
    msg['To'] = 'admin@empresa.com'            # Destinatário Fictício

    try:
        # Conecta no container 'smtp-alvo' na porta 1025 (Padrão do MailHog)
        # Não precisa de senha nem SSL
        s = smtplib.SMTP('smtp-alvo', 1025)
        s.send_message(msg)
        s.quit()
        print(f"✅ SUCESSO! Alerta enviado para o MailHog.")
    except Exception as e:
        print(f"❌ ERRO AO CONECTAR NO MAILHOG: {str(e)}")

# --- SEGURANÇA: CÁLCULO DE HASH ---
def calcular_hash_arquivo(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, "rb") as f:
        bytes = f.read()
        return hashlib.md5(bytes).hexdigest()

# Inicialização da Segurança
if os.path.exists(ARQUIVO_VIGIADO):
    HASH_ORIGINAL = calcular_hash_arquivo(ARQUIVO_VIGIADO)
    print(f"🔒 Segurança iniciada. Hash: {HASH_ORIGINAL}")
else:
    with open(ARQUIVO_VIGIADO, 'w') as f:
        f.write("config=padrao")
    HASH_ORIGINAL = calcular_hash_arquivo(ARQUIVO_VIGIADO)
    print(f"⚠️ Arquivo criado. Hash: {HASH_ORIGINAL}")

# --- SENSORES ---

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
    
    # Lógica de Disparo
    if ULTIMO_STATUS["web"] and not resultado["status_online"]:
        enviar_alerta_email("Web Server CAIU", resultado["detalhes"])
        ULTIMO_STATUS["web"] = False
    elif not ULTIMO_STATUS["web"] and resultado["status_online"]:
        ULTIMO_STATUS["web"] = True
        
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

    if ULTIMO_STATUS["db"] and not resultado["status_online"]:
        enviar_alerta_email("Banco de Dados CAIU", resultado["detalhes"])
        ULTIMO_STATUS["db"] = False
    elif not ULTIMO_STATUS["db"] and resultado["status_online"]:
        ULTIMO_STATUS["db"] = True
        
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

    if ULTIMO_STATUS["smtp"] and not resultado["status_online"]:
        enviar_alerta_email("Servidor SMTP (MailHog) CAIU", resultado["detalhes"])
        ULTIMO_STATUS["smtp"] = False
    elif not ULTIMO_STATUS["smtp"] and resultado["status_online"]:
        ULTIMO_STATUS["smtp"] = True
        
    return resultado

def checar_seguranca_arquivo():
    hash_atual = calcular_hash_arquivo(ARQUIVO_VIGIADO)
    status_seguro = True
    mensagem = "Integridade verificada. Arquivo original."
    
    if hash_atual != HASH_ORIGINAL:
        status_seguro = False
        mensagem = f"PERIGO: O arquivo '{ARQUIVO_VIGIADO}' foi alterado!"

    if ULTIMO_STATUS["seguranca"] and not status_seguro:
        enviar_alerta_email("VIOLAÇÃO DE SEGURANÇA", mensagem)
        ULTIMO_STATUS["seguranca"] = False
    elif not ULTIMO_STATUS["seguranca"] and status_seguro:
        ULTIMO_STATUS["seguranca"] = True
        
    return {"servico": "Integridade de Arquivos", "status_online": status_seguro, "latencia_ms": 0, "detalhes": mensagem}

# --- ROTAS ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/monitorar')
def monitorar():
    r1 = checar_web_server()
    r2 = checar_banco_dados()
    r3 = checar_smtp()
    r4 = checar_seguranca_arquivo()
    return jsonify([r1, r2, r3, r4])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)