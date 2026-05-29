# 🌐 Projeto de Redes: Análise de Desempenho TCP vs. R-UDP (Go-Back-N)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![Wireshark](https://img.shields.io/badge/Wireshark-Captures-1679A7)
![Redes](https://img.shields.io/badge/Disciplina-Redes_de_Computadores-success)

Este repositório contém a entrega completa da Fase 1 do projeto da disciplina de Redes de Computadores. O objetivo central deste trabalho é projetar, implementar e validar um protocolo de transporte confiável sobre UDP (denominado **R-UDP**) operando na camada de aplicação, utilizando a técnica de janela deslizante **Go-Back-N**. 

Além da implementação, o projeto realiza uma profunda análise estatística comparando o protocolo R-UDP com o **TCP** padrão do sistema operativo, submetendo ambos a cenários de anomalias de rede (perda de pacotes e atraso) forjados via ferramenta `tc` (Traffic Control) no Linux.

---

## 👤 Autor
- **Erik Vinicius Lustosa Da Silva**
- Matrícula: 20261005065
- GitHub: [@eriklustosa](https://github.com/eriklustosa)

---

## 📁 Estrutura Completa do Repositório

A arquitetura do projeto foi dividida num ambiente contentorizado (Docker) para isolar o Cliente e o Servidor, garantindo que os testes de rede não sofram interferências do sistema operativo hospedeiro.

    projeto_redes/
    ├── client/
    │   ├── client_tcp.py         # Script do cliente TCP
    │   ├── client_rudp.py        # Script do cliente implementando Go-Back-N
    │   └── teste_10mb.dat        # Ficheiro de carga útil (payload) de 10MB
    ├── server/
    │   ├── server_tcp.py         # Script do servidor TCP 
    │   ├── server_rudp.py        # Script do servidor R-UDP (ordenação e ACKs)
    │   ├── recebido_tcp.dat      # Ficheiro de saída (runtime)
    │   └── recebido_rudp.dat     # Ficheiro de saída (runtime)
    ├── capturas/                 # Dumps de rede (.pcap) comprobatórios
    ├── Dockerfile                # Instruções da imagem Docker
    ├── docker-compose.yml        # Topologia de rede virtual (172.19.0.0/16)
    └── README.md                 # Documentação principal

---

## ⚙️ Características Técnicas e Implementação

### 1. Protocolo R-UDP (Go-Back-N)
O R-UDP foi desenvolvido de raiz utilizando Sockets UDP (`SOCK_DGRAM`) e apenas bibliotecas nativas do Python. Para garantir a entrega íntegra dos 10MB, implementou-se:
* **Numeração de Sequência:** Cada datagrama carrega um cabeçalho customizado (4 bytes para o número de sequência).
* **Janela Deslizante:** O cliente envia pacotes até o limite da janela de transmissão antes de bloquear.
* **ACK Cumulativo/Individual:** O servidor responde com reconhecimentos em ordem.
* **Mecanismo de Timeout:** Se um ACK falha ou o tempo expira, o cliente retransmite a janela inteira (comportamento base do Go-Back-N).

### 2. Cabeçalho de Autenticação Customizado
A camada de aplicação injeta um cabeçalho explícito de autenticação nos primeiros pacotes:
`X-Custom-Auth: 20261005065 - Erik Vinicius Lustosa Da Silva`
*(Validação efetuada via Wireshark utilizando o filtro: `frame contains "Erik"`).*

---

## 🛠️ Procedimentos de Teste e Ferramentas

### Geração do Ficheiro de Teste (Dummy File)
Para garantir que o ficheiro de 10MB continha dados aleatórios e não fosse comprimido indevidamente pela rede, foi gerado via terminal Linux através do comando:
`dd if=/dev/urandom of=client/teste_10mb.dat bs=1M count=10`

### Simulação de Anomalias (Traffic Control)
A validação de desempenho utilizou o módulo `netem` do Linux. Os cenários aplicados na interface `eth0` do cliente foram:

| Cenário | Perda de Pacotes | Atraso (Delay) | Comando `tc` utilizado |
| :--- | :---: | :---: | :--- |
| **Cenário A** | 0% | 10ms | `tc qdisc add dev eth0 root netem delay 10ms` |
| **Cenário B** | 10% | 50ms | `tc qdisc change dev eth0 root netem delay 50ms loss 10%` |
| **Cenário C** | 20% | 100ms | `tc qdisc change dev eth0 root netem delay 100ms loss 20%` |

### Captura de Tráfego (TCPDump)
Todos os ficheiros `.pcap` presentes na diretoria `/capturas` foram gerados diretamente nos contentores durante a transmissão, utilizando comandos de escuta promíscua. Exemplo para o R-UDP:
`tcpdump -i eth0 udp port 5001 -w /capturas/cenario_a_rudp.pcap`

---

## 📈 Resultados da Validação Cruzada (TCPDump vs. Aplicação)

### Performance do TCP (Controle de Congestionamento nativo)
| Cenário | Tempo Medido (Python) | Tempo de Rede (Wireshark) | Volume Trafegado |
| :--- | :--- | :--- | :--- |
| **Cenário A (0% Perda)** | 0.6638 s | 0.6900 s | 6.212.105 bytes |
| **Cenário B (10% Perda)** | 142.3782 s | 142.4900 s | 11.107.627 bytes |
| **Cenário C (20% Perda)** | 522.6606 s | 523.1860 s | 11.320.925 bytes |

### Performance do R-UDP (Go-Back-N)
| Cenário | Tempo Medido (Python) | Tempo de Rede (Wireshark) | Volume Trafegado |
| :--- | :--- | :--- | :--- |
| **Cenário A (0% Perda)** | 3.3727 s | 3.3720 s | 3.993.878 bytes |
| **Cenário B (10% Perda)** | 541.6891 s | 541.6870 s | 13.213.478 bytes |
| **Cenário C (20% Perda)** | 1557.8811 s | 1557.8830 s | 21.210.038 bytes |

**Conclusão Estatística:**
O algoritmo Go-Back-N (R-UDP) sofre degradação extrema em redes instáveis. No Cenário C (20% de perda), o reenvio de janelas inteiras devido a timeouts gerou 21.2 MB de tráfego na rede apenas para transferir os 10MB originais, demorando quase 26 minutos. O protocolo TCP, beneficiando de mecanismos avançados como o SACK (Selective Acknowledgment), mitigou as perdas reenviando pacotes específicos, gerando apenas 11.3 MB de tráfego e concluindo a transferência em 1/3 do tempo do R-UDP.

*(Nota: Os gráficos de linha comparativos gerados com a biblioteca Matplotlib encontram-se detalhados no Relatório Final do projeto).*

---

## 🚀 Como Executar o Projeto Localmente

**1. Clonar o Repositório:**

    git clone https://github.com/eriklustosa/projeto-redes-fase1.git
    cd projeto-redes-fase1

**2. Construir a Infraestrutura Docker:**

    docker-compose up -d --build

**3. Executar o Servidor (Aguardando conexões):**

    docker exec -it redes_servidor bash
    python3 server_rudp.py

**4. Iniciar a Transferência no Cliente (Simulando o Cenário B):**

    docker exec -it redes_cliente bash
    tc qdisc replace dev eth0 root netem delay 50ms loss 10%
    python3 client_rudp.py

**5. Encerrar e Limpar o Ambiente:**
Após os testes, encerre os contentores e limpe as redes virtuais executando:

    docker-compose down
