import socket

HOST = '127.0.0.1'
PORT = 12345 

def cliente_monitor():
    #Implementa o Cliente de Monitoramento do Sistema.
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        cliente_socket.connect((HOST, PORT))
        print(f"Conectado ao Servidor de Monitoramento em {HOST}:{PORT}")
        print("-" * 30)
        print("Comandos disponíveis:")
        print("1: GET CPU")
        print("2: GET MEMORY")
        print("3: GET PROCESSES")
        print("4: SAIR")
        print("-" * 30)
        
        while True:
            comando_input = input("Digite o número do comando (1-4): ")
            
            if comando_input == '1':
                comando = 'GET CPU'
            elif comando_input == '2':
                comando = 'GET MEMORY'
            elif comando_input == '3':
                comando = 'GET PROCESSES'
            elif comando_input == '4':
                comando = 'SAIR'
            else:
                print("Opção inválida.")
                continue

            # Envia o comando
            cliente_socket.sendall(comando.encode('utf-8'))
            
            if comando == 'SAIR':
                break

            # Recebe resposta
            resposta = cliente_socket.recv(4096).decode('utf-8') # Aumenta o buffer para comandos longos
            print("-" * 30)
            print(f"STATUS DO SERVIDOR:\n{resposta}")
            print("-" * 30)

    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar. Certifique-se de que o servidor está em execução.")
    
    finally:
        # Encerra conexão
        cliente_socket.close()
        print("Conexão encerrada.")

if __name__ == "__main__":
    cliente_monitor()