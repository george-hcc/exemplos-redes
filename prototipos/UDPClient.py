# -*- coding: utf-8 -*-

# Importa módulo socket, que forma base das comunicações em rede em Python
import socket as sk

# Define nome (ou IP) e número de porta do processo servidor
serverName = '127.0.0.1'
serverPort = 12000

# Cria soquete UDP do cliente
clientSocket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM) 

# raw_input() é função do Python que lê mensagem digitada com teclado e atribui à variável message
message = input('Sentença de entrada (letras minúsculas):')

# sendto() acrescenta endereço de destino (serverName, serverPort) à mensagem e envia pacote pelo soquete
clientSocket.sendto(message.encode('utf-8'), (serverName, serverPort)) 

# Quando pacote é recebido pelo soquete do cliente, dados são atribuídos a modifiedMessage e endereço de origem a serverAddress
modifiedMessage, serverAddress = clientSocket.recvfrom(2048) 

# Imprime modifiedMessage na tela
print(modifiedMessage.decode('utf-8'))

# Fecha soquete do cliente
clientSocket.close()

