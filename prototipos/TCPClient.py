# -*- coding: utf-8 -*-

# Importa módulo socket, que forma base das comunicações em rede em Python
import socket as sk

# Define nome (ou IP) e número de porta do processo servidor
serverName = '127.0.0.1'
serverPort = 21

# Cria soquete TCP do cliente
clientSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)

# Solicita estabelecimento de conexão com servidor
clientSocket.connect((serverName, serverPort))

# Lê mensagem a enviar digitada com teclado e atribui à variável message
message = input('Sentença de entrada (letras minúsculas):')

# send() envia mensagem pelo soquete TCP
clientSocket.send(message.encode('utf-8'))

# Quando pacote é recebido pelo soquete do cliente, dados são atribuídos a modifiedMessage
modifiedMessage = clientSocket.recv(1024) 

# Imprime modifiedMessage na tela
print(modifiedMessage.decode('utf-8'))

# Fecha soquete do cliente
clientSocket.close()

