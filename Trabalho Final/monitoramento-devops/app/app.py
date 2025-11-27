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

# CONFIGURAÇÕES GLOBAIS
ARQUIVO_VIGIADO = "protegido.conf"
HASH_ORIGINAL = "" 
LIMITE_LATENCIA_AMARELO = 2000
SIMULAR_LENTIDAO = False

ULTIMO_STATUS = {
    "web": "ok",
    "db": "ok", 
    "smtp": "ok", 
    "seguranca": "ok"
}

# FUNÇÃO DE ENVIAR E-MAIL
def enviar_alerta_email(titulo, mensagem, nivel="CRÍTICO"):
    print(f"📧 Enviando alerta ({nivel}) para MailHog: {titulo}...")
    
    msg = MIMEText(f"""
    SISTEMA DE MONITORAMENTO DEVOPS
    -------------------------------
    Nível do Alerta: {nivel}
    Evento: {titulo}
    Data/Hora: {datetime.now()}
    
    Detalhes Técnicos:
    {mensagem}
    """)
    
    msg['Subject'] = f'🚨 [{nivel}] {titulo}'
    msg['From'] = 'sistema@monitoramento.local'
    msg['To'] = 'admin@empresa.com'

    try:
        s = smtplib.SMTP('smtp-alvo', 1025)
        s.send_message(msg)
        s.quit()
        print(f"✅ E-mail enviado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao conectar no MailHog: {str(e)}")

# SEGURANÇA
def calcular_hash_arquivo(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, "rb") as f:
        bytes = f.read()
        return hashlib.md5(bytes).hexdigest()

if os.path.exists(ARQUIVO_VIGIADO):
    HASH_ORIGINAL = calcular_hash_arquivo(ARQUIVO_VIGIADO)
    print(f"🔒 Segurança iniciada. Hash original: {HASH_ORIGINAL}")
else:
    with open(ARQUIVO_VIGIADO, 'w') as f:
        f.write("config=padrao")
    HASH_ORIGINAL = calcular_hash_arquivo(ARQUIVO_VIGIADO)
    print(f"⚠️ Arquivo de segurança criado. Hash: {HASH_ORIGINAL}")

# SENSORES DE SERVIÇOS

def checar_web_server():
    url = "http://web-alvo"
    resultado = {
        "servico": "Web Server (Nginx)", 
        "status_online": False, 
        "latencia_ms": 0, 
        "detalhes": "",
        "nivel_alerta": "critico"
    }
    
    try:
        inicio = time.time()
        
        if SIMULAR_LENTIDAO:
            time.sleep(2.5)

        requests.get(url, timeout=5)
        fim = time.time()
        
        latencia = round((fim - inicio) * 1000, 2)
        resultado["latencia_ms"] = latencia
        resultado["status_online"] = True
        
        if latencia > LIMITE_LATENCIA_AMARELO:
            resultado["nivel_alerta"] = "atencao"
            resultado["detalhes"] = f"LENTIDÃO DETECTADA: {latencia}ms"
        else:
            resultado["nivel_alerta"] = "ok"
            resultado["detalhes"] = "HTTP 200 OK - Performance Normal"
            
    except Exception as e:
        resultado["nivel_alerta"] = "critico"
        resultado["detalhes"] = str(e)
    
    verificar_e_enviar_alerta("web", resultado)
    return resultado

def checar_banco_dados():
    resultado = {"servico": "Banco de Dados (Postgres)", "status_online": False, "latencia_ms": 0, "detalhes": "", "nivel_alerta": "critico"}
    try:
        inicio = time.time()
        conn = psycopg2.connect(host="db-alvo", user="postgres", password="senha_secreta", connect_timeout=3)
        conn.close()
        fim = time.time()
        resultado["status_online"] = True
        resultado["latencia_ms"] = round((fim - inicio) * 1000, 2)
        resultado["detalhes"] = "Conexão aceita"
        resultado["nivel_alerta"] = "ok"
    except Exception as e:
        resultado["detalhes"] = str(e)

    verificar_e_enviar_alerta("db", resultado)
    return resultado

def checar_smtp():
    resultado = {"servico": "Servidor SMTP (MailHog)", "status_online": False, "latencia_ms": 0, "detalhes": "", "nivel_alerta": "critico"}
    try:
        inicio = time.time()
        s = smtplib.SMTP('smtp-alvo', 1025, timeout=3)
        s.quit()
        fim = time.time()
        resultado["status_online"] = True
        resultado["latencia_ms"] = round((fim - inicio) * 1000, 2)
        resultado["detalhes"] = "Serviço SMTP respondendo"
        resultado["nivel_alerta"] = "ok"
    except Exception as e:
        resultado["detalhes"] = str(e)

    verificar_e_enviar_alerta("smtp", resultado)
    return resultado

def checar_seguranca_arquivo():
    hash_atual = calcular_hash_arquivo(ARQUIVO_VIGIADO)
    resultado = {"servico": "Integridade de Arquivos", "status_online": True, "latencia_ms": 0, "detalhes": "Integridade verificada.", "nivel_alerta": "ok"}
    
    if hash_atual != HASH_ORIGINAL:
        resultado["status_online"] = False
        resultado["nivel_alerta"] = "critico"
        resultado["detalhes"] = f"PERIGO: O arquivo '{ARQUIVO_VIGIADO}' foi alterado!"

    verificar_e_enviar_alerta("seguranca", resultado)
    return resultado

# LÓGICA CENTRAL DE ALERTAS
def verificar_e_enviar_alerta(chave, resultado):
    estado_atual = resultado["nivel_alerta"]
    estado_anterior = ULTIMO_STATUS[chave]

    if estado_atual != estado_anterior:
        if estado_atual == "atencao":
            enviar_alerta_email(f"{resultado['servico']} - DEGRADAÇÃO", resultado["detalhes"], "ATENÇÃO")
        elif estado_atual == "critico":
            enviar_alerta_email(f"{resultado['servico']} - FALHA", resultado["detalhes"], "CRÍTICO")
        
        ULTIMO_STATUS[chave] = estado_atual

# ROTAS

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