import os
import hashlib
import smtplib
import socket
import time
import random
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# --- CONFIGURAÇÕES DO AMBIENTE DOCKER ---
SERVICES = {
    'web': {'host': 'web-alvo', 'port': 80, 'name': 'Web Server Nginx'},
    'db':  {'host': 'db-alvo', 'port': 5432, 'name': 'Banco de Dados SQL'},
    'smtp': {'host': 'smtp-alvo', 'port': 1025, 'name': 'SMTP MailHog'},
}

# Configurações de E-mail
SMTP_SENDER_HOST = 'smtp-alvo'
SMTP_SENDER_PORT = 1025
FILE_TO_WATCH = 'protegido.conf'

# Estado Global
last_file_hash = None
security_status = "NORMAL"

# --- FUNÇÕES ---

def get_service_status(host, port):
    """
    1. Tenta conexão REAL (TCP).
    2. Se falhar -> Retorna OFFLINE (Vermelho).
    3. Se conectar -> Tem 10% de chance de simular latência alta (Amarelo).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    start_time = time.time()
    
    try:
        # Tenta conectar de verdade
        s.connect((host, port))
        real_ping = int((time.time() - start_time) * 1000)
        s.close()

        # --- LÓGICA DE SIMULAÇÃO DE DEGRADAÇÃO (NÍVEL 2 - AMARELO) ---
        # 10% de chance de simular lentidão (anomalia de tráfego)
        if random.randint(1, 100) > 90:
            fake_latency = random.randint(250, 800) # Latência alta simulada
            return fake_latency, 'ONLINE'
        
        return real_ping, 'ONLINE'

    except:
        return 0, 'OFFLINE'

def calculate_file_hash(filepath):
    if not os.path.exists(filepath): return None
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def send_email_alert(service_name, status, details):
    """Envia e-mail para o MailHog"""
    try:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        subject = f"ALERTA [{status}]: {service_name}"
        
        body = f"""
        ========================================
        SISTEMA DE MONITORAMENTO DEVOPS
        ========================================
        
        SERVIÇO AFETADO: {service_name}
        NOVO STATUS:     {status}
        HORÁRIO:         {timestamp}
        
        DETALHES TÉCNICOS:
        {details}
        
        AÇÃO RECOMENDADA:
        - Verificar logs do container
        - Checar balanceador de carga
        ========================================
        """
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = 'monitor@devops.local'
        msg['To'] = 'admin@devops.local'

        server = smtplib.SMTP(SMTP_SENDER_HOST, SMTP_SENDER_PORT)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
        print(f"📧 E-mail enviado: {service_name} -> {status}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        return False

# --- MONITORAMENTO DE SEGURANÇA (ARQUIVO) ---
def check_security_job():
    global last_file_hash, security_status
    current_hash = calculate_file_hash(FILE_TO_WATCH)
    
    if last_file_hash is None:
        last_file_hash = current_hash
        return

    # Se o hash mudou, dispara alerta CRÍTICO
    if current_hash != last_file_hash:
        security_status = "CRITICO"
        last_file_hash = current_hash
        send_email_alert("SEGURANÇA & INTEGRIDADE", "CRÍTICO", f"O arquivo de configuração '{FILE_TO_WATCH}' foi modificado não-autorizado.")

scheduler = BackgroundScheduler()
scheduler.add_job(check_security_job, 'interval', seconds=5)
scheduler.start()

# --- ROTAS DA API ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_real_status():
    data = {}
    
    for key, config in SERVICES.items():
        ping, status = get_service_status(config['host'], config['port'])
        
        status_level = 'NORMAL' # Verde
        
        if status == 'OFFLINE':
            status_level = 'CRITICO' # Vermelho (Container parado)
        elif ping > 200: 
            status_level = 'ATENCAO' # Amarelo (Latência alta simulada ou real)
            
        data[key] = {
            'ping': ping,
            'status_text': status,
            'level': status_level
        }

    # Adiciona status de segurança
    data['sec'] = {
        'status_text': 'INVASÃO' if security_status == 'CRITICO' else 'PROTEGIDO',
        'level': security_status
    }

    return jsonify(data)

@app.route('/api/trigger-email', methods=['POST'])
def trigger_email():
    """Rota chamada pelo Front-end para garantir envio de e-mail"""
    d = request.json
    send_email_alert(d['servico'], d['status'], d['msg'])
    return jsonify({"ok": True})

if __name__ == '__main__':
    # Cria hash inicial
    last_file_hash = calculate_file_hash(FILE_TO_WATCH)
    print("🚀 Monitoramento Iniciado...")
    app.run(host='0.0.0.0', port=5000, debug=True)