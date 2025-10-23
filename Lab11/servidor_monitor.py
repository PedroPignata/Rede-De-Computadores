import socket
import psutil
from datetime import datetime
import time

HOST = '127.0.0.1'
PORT = 12346 

def servidor_monitor():
    #Servidor de Monitoramento de Saúde do Sistema.
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        servidor_socket.bind((HOST, PORT))
        servidor_socket.listen(1)
        print(f"Servidor de Monitoramento pronto! Escutando em {HOST}:{PORT}")
        
        # Aceita conexão (para este modelo simples, apenas um cliente por vez)
        conexao, endereco = servidor_socket.accept()
        print(f"Cliente conectado: {endereco}")
        
        try:
            while True:
                # Recebe mensagem (comandos)
                dados = conexao.recv(1024)
                if not dados:
                    break
                
                comando = dados.decode('utf-8').strip().upper()
                print(f"Comando recebido: {comando}")
                
                resposta = processar_comando(comando)
                
                # Envia resposta
                conexao.sendall(resposta.encode('utf-8'))

        except Exception as e:
            print(f"Erro na comunicação com o cliente: {e}")
        
        finally:
            # Encerra conexão do cliente
            conexao.close()
            print(f"Conexão com {endereco} encerrada.")

    except socket.error as e:
        print(f"Erro no socket: {e}")
    
    finally:
        # Encerra socket do servidor
        servidor_socket.close()
        print("Servidor encerrado.")


def processar_comando(comando):
    #Monitoramento na qual a função for escolhida
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if comando == 'GET CPU':
        # Obtem o uso da CPU durante 1 segundo
        uso_cpu = psutil.cpu_percent(interval=1)
        return f"[{timestamp}] CPU_USAGE: {uso_cpu:.1f}%"
    
    elif comando == 'GET MEMORY':
        memoria = psutil.virtual_memory()
        total_gb = memoria.total / (1024**3)
        uso_gb = memoria.used / (1024**3)
        percentual = memoria.percent
        
        resposta = (
            f"[{timestamp}] MEMORY_TOTAL: {total_gb:.2f} GB | "
            f"MEMORY_USED: {uso_gb:.2f} GB | "
            f"MEMORY_PERCENT: {percentual:.1f}%"
        )
        return resposta

    elif comando == 'GET PROCESSES':
        # Obtem os processos ordenados por uso de CPU
        top_processos = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            top_processos.append(proc.info)

        # Ordena a lista de processos pelo uso de CPU
        top_processos.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        # Formata os 5 primeiros processos
        lista_formatada = ["--- TOP 5 PROCESSOS ---"]
        for i, proc in enumerate(top_processos[:5]):
            lista_formatada.append(f"{i+1}. PID: {proc['pid']} | CPU: {proc['cpu_percent']:.1f}% | Nome: {proc['name']}")
        
        return f"[{timestamp}] " + " | ".join(lista_formatada)

    elif comando == 'SAIR':
        return "SAIR"
        
    else:
        return (
            f"[{timestamp}] ERRO: Comando inválido. "
            "Use GET CPU, GET MEMORY, GET PROCESSES ou SAIR."
        )

if __name__ == "__main__":
    servidor_monitor()