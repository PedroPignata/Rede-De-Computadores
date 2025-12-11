import os
import hashlib
import smtplib
import socket
import time
import random
import json
from threading import Lock
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# ambiente de monitoramento docker
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

# alertas 
ALERTS_FILE = 'alerts.json'
MAX_ALERTS_STORED = 1000
alerts_lock = Lock()

# Histórico de status (para cálculo de % de segurança)
STATUS_HISTORY_FILE = 'status_history.json'
status_lock = Lock()
STATUS_HISTORY_WINDOW = 100 

# Rate limit de e-mails
EMAIL_MIN_INTERVAL = 10
email_last_sent = {}
email_last_sent_lock = Lock()

# Utilitários de persistência

def load_json_file(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler {path}: {e}")
        return []

def save_json_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar {path}: {e}")

# alertas
def load_alerts():
    return load_json_file(ALERTS_FILE)

def save_alerts(alerts):
    try:
        if len(alerts) > MAX_ALERTS_STORED:
            alerts = alerts[-MAX_ALERTS_STORED:]
        save_json_file(ALERTS_FILE, alerts)
    except Exception as e:
        print("Erro ao salvar alerts.json:", e)

def append_alert(service_name, level, details):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert = {
        'timestamp': ts,
        'service': service_name,
        'level': level,
        'details': details
    }
    with alerts_lock:
        alerts = load_alerts()
        alerts.append(alert)
        save_alerts(alerts)
    print(f"🗂️ Alerta registrado: {alert}")
    return alert

# historico status
def load_status_history():
    return load_json_file(STATUS_HISTORY_FILE)

def save_status_history(history):
    try:
        if len(history) > STATUS_HISTORY_WINDOW * 5:  
            history = history[-STATUS_HISTORY_WINDOW*5:]
        save_json_file(STATUS_HISTORY_FILE, history)
    except Exception as e:
        print("Erro ao salvar status_history.json:", e)

def append_status_snapshot(snapshot):

    with status_lock:
        hist = load_status_history()
        hist.append(snapshot)
        save_status_history(hist)

def compute_secure_pct(service_key, window=STATUS_HISTORY_WINDOW):

    with status_lock:
        hist = load_status_history()
        if not hist:
            return 100  
        last = hist[-window:]
        total = 0
        normal_count = 0
        for s in last:
            if service_key in s:
                total += 1
                if s[service_key] == 'NORMAL':
                    normal_count += 1
        if total == 0:
            return 100
        return int((normal_count / total) * 100)

# Funções de monitor

def get_service_status(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2.0)
    start_time = time.time()
    
    try:
        s.connect((host, port))
        real_ping = int((time.time() - start_time) * 1000)
        s.close()

        # Simulação de degradação (10%)
        if random.randint(1, 100) > 90:
            fake_latency = random.randint(250, 800)
            return fake_latency, 'ONLINE'
        
        return real_ping, 'ONLINE'

    except:
        return 0, 'OFFLINE'

def calculate_file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# Envio de e-mail 

def can_send_email_for_service(service_name):

    now = time.time()
    with email_last_sent_lock:
        last = email_last_sent.get(service_name)
        if last is None:
            email_last_sent[service_name] = now
            return True
        if now - last >= EMAIL_MIN_INTERVAL:
            email_last_sent[service_name] = now
            return True
        return False

def send_email_alert(service_name, status, details):

    allowed = can_send_email_for_service(service_name)
    if not allowed:
        # registra alerta mas marca rate limiting
        append_alert(service_name, status + " (RATE_LIMITED)", details + " | Envio ignorado por rate-limit")
        print(f"⏱️ Email rate-limited para {service_name}, não será enviado agora.")
        return False

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
        """
        
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = 'monitor@devops.local'
        msg['To'] = 'admin@devops.local'

        server = smtplib.SMTP(SMTP_SENDER_HOST, SMTP_SENDER_PORT)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
        server.quit()
        print(f"📧 E-mail enviado: {service_name} -> {status}")

        append_alert(service_name, status, details)
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        append_alert(service_name, status + " (EMAIL_FAIL)", f"{details} | erro: {e}")
        return False

# Monitor de integridad

def check_security_job():
    global last_file_hash, security_status

    current_hash = calculate_file_hash(FILE_TO_WATCH)

    if last_file_hash is None:
        last_file_hash = current_hash
        return

    if current_hash != last_file_hash:
        security_status = "CRITICO"
        last_file_hash = current_hash
        send_email_alert("SEGURANÇA & INTEGRIDADE", "CRÍTICO", f"Arquivo '{FILE_TO_WATCH}' foi modificado.")
    else:

        security_status = "NORMAL"

# Agenda de verificação
scheduler = BackgroundScheduler()
scheduler.add_job(check_security_job, 'interval', seconds=10)  # --> 10s
scheduler.start()


# Rotas da API

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status')
def get_real_status():
    data = {}
    snapshot = {'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    for key, config in SERVICES.items():
        ping, status_text = get_service_status(config['host'], config['port'])
        
        level = 'NORMAL'
        if status_text == 'OFFLINE':
            level = 'CRITICO'
        elif ping > 200:
            level = 'ATENCAO'

        data[key] = {
            'ping': ping,
            'status_text': status_text,
            'level': level,
            # secure_pct calculado com base no histórico
            'secure_pct': compute_secure_pct(key)
        }

        snapshot[key] = level

    # segurança
    data['sec'] = {
        'status_text': 'INVASÃO' if security_status == 'CRITICO' else 'PROTEGIDO',
        'level': security_status,
        'secure_pct': compute_secure_pct('sec')
    }
    snapshot['sec'] = data['sec']['level']

    # salvar snapshot para cálculo de % ao longo do tempo
    append_status_snapshot(snapshot)

    return jsonify(data)


@app.route('/api/trigger-email', methods=['POST'])
def trigger_email():
    d = request.json
    send_email_alert(d['servico'], d['status'], d['msg'])
    return jsonify({"ok": True})


@app.route('/api/alerts')
def api_alerts():

    return jsonify({"alerts": load_alerts()})


@app.route('/api/alerts/clear', methods=['POST'])
def clear_alerts():
    save_alerts([])
    return jsonify({"ok": True})

# Inicialização

if __name__ == '__main__':
    # garante arquivos existem
    if not os.path.exists(ALERTS_FILE):
        save_alerts([])
    if not os.path.exists(STATUS_HISTORY_FILE):
        save_status_history([])

    last_file_hash = calculate_file_hash(FILE_TO_WATCH)
    print("🚀 Monitoramento Iniciado (check_security a cada 10s)...")
    app.run(host='0.0.0.0', port=5000, debug=True)