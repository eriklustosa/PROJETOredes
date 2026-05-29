import socket
import time
import struct
import hashlib

HOST = '0.0.0.0'
PORT = 5001 # Usando uma porta diferente do TCP
PACKET_FORMAT = '!I 32s' # Inteiro (4 bytes) + String de 32 bytes (MD5)
HEADER_SIZE = struct.calcsize(PACKET_FORMAT)

def verify_checksum(data, received_checksum):
    return hashlib.md5(data).hexdigest().encode() == received_checksum

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"[*] Servidor R-UDP (Go-Back-N) escutando na porta {PORT}...")
        
        expected_seq = 0
        received_bytes = 0
        start_time = None
        header_received = False

        with open("/app/recebido_rudp.dat", "wb") as f:
            while True:
                try:
                    s.settimeout(5.0) # Timeout longo apenas para encerrar se o cliente sumir
                    packet, addr = s.recvfrom(4096 + HEADER_SIZE)
                    
                    if not packet:
                        break
                        
                    # Sinal de encerramento da transferência
                    if len(packet) == 2 and packet == b'F!':
                        s.sendto(b'ACK_FIN', addr)
                        break
                        
                    # 1. Desempacotando cabeçalho customizado do nosso protocolo
                    header = packet[:HEADER_SIZE]
                    data = packet[HEADER_SIZE:]
                    seq_num, checksum = struct.unpack(PACKET_FORMAT, header)
                    
                    # 2. Validação de Integridade (Checksum)
                    if verify_checksum(data, checksum):
                        # 3. Validação de Ordem (Go-Back-N)
                        if seq_num == expected_seq:
                            if not header_received:
                                print(f"[+] Cabeçalho de Autenticação recebido:\n{data.decode('utf-8', errors='ignore')}")
                                header_received = True
                                start_time = time.time()
                            else:
                                f.write(data)
                                received_bytes += len(data)
                            
                            # Envia ACK do pacote processado com sucesso
                            ack_packet = struct.pack('!I', expected_seq)
                            s.sendto(ack_packet, addr)
                            expected_seq += 1
                        else:
                            # Se chegou fora de ordem, reenvia o ACK do último pacote correto
                            ack_packet = struct.pack('!I', expected_seq - 1)
                            s.sendto(ack_packet, addr)
                    else:
                        print(f"[-] Pacote corrompido! Checksum falhou para a seq {seq_num}")
                        
                except socket.timeout:
                    if received_bytes > 0:
                        print("[*] Timeout de recepção alcançado.")
                        break

        end_time = time.time()
        tempo_total = end_time - start_time if start_time else 0
        throughput = (received_bytes * 8 / 1e6) / tempo_total if tempo_total > 0 else 0
        
        print("-" * 30)
        print("Transferência R-UDP Concluída!")
        print(f"Tamanho: {received_bytes} bytes")
        print(f"Tempo: {tempo_total:.4f} segundos")
        print(f"Throughput: {throughput:.2f} Mbps")

if __name__ == "__main__":
    start_server()