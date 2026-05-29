import socket
import time

HOST = '0.0.0.0'
PORT = 5000

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Servidor TCP escutando na porta {PORT}...")
        
        conn, addr = s.accept()
        with conn:
            print(f"[+] Conectado por {addr}")
            
            # 1. Recebendo e exibindo o cabeçalho obrigatório
            header = conn.recv(1024).decode('utf-8')
            print(f"[+] Cabeçalho recebido:\n{header}")
            
            start_time = time.time()
            received_bytes = 0
            
            # 2. Recebendo o arquivo
            with open("/app/recebido_tcp.dat", "wb") as f:
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    f.write(data)
                    received_bytes += len(data)
                    
            end_time = time.time()
            tempo_total = end_time - start_time
            # Cálculo de Throughput em Megabits por segundo (Mbps)
            throughput = (received_bytes * 8 / 1e6) / tempo_total if tempo_total > 0 else 0
            
            print("-" * 30)
            print("Transferência TCP Concluída!")
            print(f"Tamanho: {received_bytes} bytes")
            print(f"Tempo: {tempo_total:.4f} segundos")
            print(f"Throughput: {throughput:.2f} Mbps")

if __name__ == "__main__":
    start_server()