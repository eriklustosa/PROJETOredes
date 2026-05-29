import socket
import os
import time
import struct
import hashlib

HOST = 'servidor'
PORT = 5001
FILE_PATH = "/app/teste_10mb.dat"
PACKET_FORMAT = '!I 32s'
PAYLOAD_SIZE = 4096

def create_packet(seq_num, data):
    # Calcula o hash MD5 dos dados do payload
    checksum = hashlib.md5(data).hexdigest().encode()
    # Empacota: Número de Sequência + Checksum
    header = struct.pack(PACKET_FORMAT, seq_num, checksum)
    return header + data

def send_file():
    header_auth = "X-Custom-Auth: 20261005065 - Erik Vinicius Lustosa Da Silva\n\n".encode('utf-8')
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Timeout para retransmissão
        s.settimeout(0.5) 
        
        print(f"[*] Conectando ao servidor {HOST}:{PORT} via R-UDP...")
        
        # Estruturando os pacotes em memória para facilitar o acesso da janela deslizante
        packets = []
        packets.append(create_packet(0, header_auth))
        
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "rb") as f:
                seq = 1
                while chunk := f.read(PAYLOAD_SIZE):
                    packets.append(create_packet(seq, chunk))
                    seq += 1

        total_packets = len(packets)
        base = 0
        next_seq_num = 0
        window_size = 10 # Tamanho da nossa Janela Deslizante (N)
        
        start_time = time.time()
        
        while base < total_packets:
            # 1. Envia rajada de pacotes até o limite da janela
            while next_seq_num < base + window_size and next_seq_num < total_packets:
                s.sendto(packets[next_seq_num], (HOST, PORT))
                next_seq_num += 1
                
            try:
                # 2. Aguarda os ACKs do servidor
                ack_data, _ = s.recvfrom(1024)
                ack_num = struct.unpack('!I', ack_data)[0]
                
                # 3. ACK Cumulativo: avança a base da janela
                if ack_num >= base:
                    base = ack_num + 1
                    
            except socket.timeout:
                # 4. Timeout: Ocorreu perda de pacote ou do ACK. Aciona o "Go-Back-N"
                print(f"[*] Timeout! Retransmitindo janela a partir do pacote {base}")
                next_seq_num = base

        # Sinal de finalização para o servidor fechar o arquivo
        s.sendto(b'F!', (HOST, PORT))
        
        print("-" * 30)
        print(f"Envio R-UDP Concluído em {time.time() - start_time:.2f}s!")

if __name__ == "__main__":
    send_file()