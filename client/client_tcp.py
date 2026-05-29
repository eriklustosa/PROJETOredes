import socket
import os
import time

HOST = 'servidor'
PORT = 5000
FILE_PATH = "/app/teste_10mb.dat"

# Criando um arquivo dummy de 10MB automaticamente para o teste
if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "wb") as f:
        f.write(os.urandom(10 * 1024 * 1024))

def send_file():
    # Cabeçalho obrigatório
    header = "X-Custom-Auth: 20261005065 - Erik Vinicius Lustosa Da Silva\n\n"
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"[*] Conectando ao servidor {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        
        # 1. Envia o cabeçalho
        s.sendall(header.encode('utf-8'))
        time.sleep(0.5) # Breve pausa para separar o cabeçalho dos dados do arquivo
        
        file_size = os.path.getsize(FILE_PATH)
        print(f"[*] Enviando arquivo de {file_size} bytes...")
        
        # 2. Envia o arquivo
        with open(FILE_PATH, "rb") as f:
            while chunk := f.read(4096):
                s.sendall(chunk)
                
        print("-" * 30)
        print("Envio TCP Concluído pelo Cliente!")

if __name__ == "__main__":
    send_file()